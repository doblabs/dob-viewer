# -*- coding: utf-8 -*-

# This file is part of 'dob'.
#
# 'dob' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'dob' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'dob'.  If not, see <http://www.gnu.org/licenses/>.
"""Facts Carousel"""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import asyncio
# (lb): We're using Click only for get_terminal_size. (The
#  UI and user interaction is otherwise all handled by PPT).
import click

from prompt_toolkit.eventloop import use_asyncio_event_loop

from nark.helpers.dev.profiling import profile_elapsed

from .action_manager import ActionManager
from .dialog_overlay import show_message
from .edits_manager import EditsManager
from .update_handler import UpdateHandler
from .zone_content import ZoneContent
from .zone_manager import ZoneManager
from ..interrogate import ask_user_for_edits
from ..helpers.exceptions import catch_action_exception
from ..helpers.re_confirm import confirm

__all__ = [
    'Carousel',
]


class Carousel(object):
    """"""
    def __init__(
        self,
        controller,
        edit_facts,
        orig_facts,
        dirty_callback,
        dry,
    ):
        self.controller = controller

        self.dry = dry

        self._avail_width = None

        self.chosen_style = None

        self.setup_async()

        self.edits_manager = EditsManager(
            controller,
            edit_facts=edit_facts,
            orig_facts=orig_facts,
            dirty_callback=dirty_callback,
            error_callback=self.error_callback,
        )

        self.action_manager = ActionManager(self)
        self.update_handler = UpdateHandler(self)
        self.zone_manager = ZoneManager(self)

    # ***

    # Magic for reset_showing_help.

    @property
    def carousel(self):
        return self

    # ***

    @property
    def chosen_style(self):
        return self._chosen_style

    @chosen_style.setter
    def chosen_style(self, chosen_style):
        self._chosen_style = chosen_style

    # ***

    @property
    def avail_width(self, force=False):
        if force or self._avail_width is None:
            self._avail_width = self.calculate_available_width()
        return self._avail_width

    def calculate_available_width(self):
        # NOTE: Without the - 2, to account for the '|' borders,
        #       app apparently hangs.
        full_width = click.get_terminal_size()[0] - 2
        if not self.chosen_style['content-width']:
            return full_width
        avail_width = min(self.chosen_style['content-width'], full_width)
        return avail_width

    # ***

    def setup_async(self):
        # 2019-01-25: (lb): We run asynchronously to support such features as
        # tick_tock_now, which keeps the ongoing fact's end clock time updated.
        # However, working with asyncio can be somewhat tricky. So, should you
        # need to disable it, here's a switch.
        self._async_enable = True
        self._confirm_exit = False
        self.asyncio_future1 = None
        self.asyncio_future2 = None

    @property
    def async_enable(self):
        return self._async_enable

    @property
    def confirm_exit(self):
        return self._confirm_exit

    @confirm_exit.setter
    def confirm_exit(self, confirm_exit):
        if confirm_exit and self.asyncio_future2 is not None:
            self.asyncio_future2.cancel()
        self._confirm_exit = confirm_exit

    # ***

    def gallop(self):
        self.standup()
        if self.async_enable:
            # Tell prompt_toolkit to use asyncio.
            use_asyncio_event_loop()
            self.event_loop = asyncio.get_event_loop()
        confirmed_facts = self.run_edit_loop()
        if self.async_enable:
            self.event_loop.close()
        return self.edits_manager.prepared_facts if confirmed_facts else []

    @property
    def prepared_facts(self):
        return self.edits_manager.prepared_facts

    # ***

    def run_edit_loop(self):
        confirmed_facts = False
        used_prompt = None
        self.enduring_edit = True
        while self.enduring_edit:
            self.runloop()
            if not self.confirm_exit:
                if self.enduring_edit:
                    used_prompt = self.prompt_fact_edits(used_prompt)
                elif not self.edits_manager.user_viewed_all_new_facts:
                    confirmed = self.process_save_early()
                    if confirmed:
                        confirmed_facts = True
                    else:
                        self.enduring_edit = True  # Keep looping.
            if self.confirm_exit:
                confirmed = self.process_exit_request()
                if not confirmed:
                    self.enduring_edit = True  # Keep looping.
            elif not self.enduring_edit:
                confirmed_facts = True  # All done; user looked at all Facts.
        return confirmed_facts

    def process_exit_request(self):
        if not self.edits_manager.is_dirty:
            # No Facts edited.
            return True
        question = _('\nReally exit without saving?')
        confirmed = confirm(question, erase_when_done=True)
        return confirmed

    def process_save_early(self):
        question = _('\nReally save without verifying all Facts?')
        confirmed = confirm(question, erase_when_done=True)
        return confirmed

    def prompt_fact_edits(self, used_prompt):
        try:
            used_prompt = self.user_prompt_edit_fact(used_prompt)
        except KeyboardInterrupt:
            self.enduring_edit = False
            self.confirm_exit = True
        else:
            self.zone_manager.rebuild_containers()
        return used_prompt

    def user_prompt_edit_fact(self, used_prompt):
        edit_fact = self.edits_manager.undoable_editable_fact(what='prompt-user')
        used_prompt = self.prompt_user(edit_fact, used_prompt)
        self.edits_manager.apply_edits(edit_fact)
        self.zone_manager.reset_diff_fact()
        return used_prompt

    def prompt_user(self, edit_fact, used_prompt):
        used_prompt = ask_user_for_edits(
            self.controller,
            edit_fact,
            always_ask=True,
            prompt_agent=used_prompt,
            restrict_edit=self.restrict_edit,
        )
        return used_prompt

    # ***

    def standup(self):
        self.edits_manager.stand_up()
        self.zone_manager.standup()
        self.update_handler.standup()
        self.action_manager.standup()
        self.zone_manager.build_and_show()

    # ***

    def runloop(self):
        self.confirm_exit = False
        self.enduring_edit = False
        self.restrict_edit = ''
        profile_elapsed('To dob runloop')
        if self.async_enable:
            # This call draws the app, but it doesn't run its event loop.
            run_async = self.zone_manager.application.run_async()
            self.asyncio_future1 = run_async.to_asyncio_future()
            self.asyncio_future2 = asyncio.ensure_future(self.tick_tock_now())
            tasks = [self.asyncio_future1, self.asyncio_future2]
            self.event_loop.run_until_complete(asyncio.wait(tasks))
            # PPT reuses the event_loop, so close it only on application
            # exit (and don't *not* close it, or an errant signal fires
            # later and asyncio crashes not being able to handle it).
        else:
            self.zone_manager.application.run()

    # ***

    async def tick_tock_now(self):
        """"""
        async def _tick_tock_now():
            tocking = True
            while tocking:
                tocking = await tick_tock_loop()

        async def tick_tock_loop():
            if self.asyncio_future1.done():
                return False
            if not await sleep_to_refresh():
                return False
            refresh_viewable()
            return True

        async def sleep_to_refresh():
            try:
                # (lb): I tried a few different behaviors here, e.g.,
                # longer sleep, or even only updating if only so much
                # time has passed (i.e., because we only need to update
                # the "now" time, we only need to really redraw every
                # second), but the seconds of the "now" time would visibly
                # increment unevenly. I settled around 50 msecs. and it
                # doesn't seem to make the user interaction at all sluggish.
                # ... Hahaha, whelp, 50 msecs. makes 1 CPU run 100% hot.
                # And 500 msecs. make 1 CPU run 20%, instead of 10....
                # But if sleep is ⅔ secs., seconds increment is jumpy.
                # 500 msecs. seems to work well.
                await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                return False
            except Exception as err:
                self.controller.client_logger.warning(
                    _("Unexpected async err: {}").format(err),
                )
            return True

        def refresh_viewable():
            self.zone_manager.selectively_refresh()
            self.zone_manager.application.invalidate()

        await _tick_tock_now()

    # ***

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def cancel_command(self, event):
        """"""
        self.confirm_exit = True
        self.enduring_edit = False
        event.app.exit()

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def cancel_softly(self, event):
        """"""
        # (lb): A little awkward: Meta-key combinations start with 'escape',
        # even though the user doesn't explicitly press the escape key. E.g.,
        # if you press ESC, PPT waits a moment, and if you don't press another
        # key, it invokes the callback for ESC; but if you press an escaped
        # combination that does not have a callback, e.g., if ALT-LEFT is not
        # bound, and the user presses ALT-LEFT, then the handler for ESC is
        # called (because the ALT-LEFT combination starts with an escape).
        if len(event.key_sequence) != 1:
            return
        kseq = event.key_sequence[0]
        if kseq.key == 'escape' and kseq.data != '\x1b':
            return
        # Allow easy 'q' cancel on editing existing Facts.
        # FIXME: Should allow for new_facts, too... but we don't track edited
        #        (though we do in each Fact's dirty_reasons; but we're
        #        consolidating behavior in new class, so can wait to fix).
        #        Then again, how much do I care? Import should be rare.
        if not self.edits_manager.is_dirty:
            self.confirm_exit = True
            self.enduring_edit = False
            event.app.exit()

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def finish_command(self, event):
        """"""
        event.app.exit()

    # ***

    def error_callback(self, errmsg):
        show_message(
            self.zone_manager.root,
            _('Wah wah'),
            _("dob is buggy! {0}").format(errmsg),
        )

    def show_plugin_error(self, errmsg):
        show_message(
            self.zone_manager.root,
            _('Oops!'),
            _('{0}').format(errmsg),
        )

    # ***

    def dev_breakpoint(self, event):
        if not self.controller.client_config['devmode']:
            self.controller.client_logger.warning(
                _('Please enable ‘devmode’ to use live debugging.')
            )
            return
        self.pdb_set_trace(event)

    def pdb_set_trace(self, event):
        import pdb
        # Just some convenience variables for the developer.
        # F841: local variable '...' is assigned to but never used
        edits = self.edits_manager  # noqa: F841
        facts = self.edits_manager.conjoined  # noqa: F841
        groups = self.edits_manager.conjoined.groups  # noqa: F841
        # Reset terminal I/O to fix interactive pdb stdin echo.
        self.pdb_break_enter()
        pdb.set_trace()
        pass  # Poke around; print variables; then [c]ontinue.
        self.pdb_break_leave(event)

    def pdb_break_enter(self):
        self.controller.pdb_break_enter()

    def pdb_break_leave(self, event=None):
        self.controller.pdb_break_leave()
        # Redraw everything. But don't both with invalidate, e.g.,:
        #   self.carousel.zone_manager.application.invalidate()
        # but rather find the renderer and clear that.
        # This'll also reset the cursor, so nice!
        self.controller.affirm(
            (event is None) or (event.app is self.zone_manager.application),
        )
        self.zone_manager.application.renderer.clear()

