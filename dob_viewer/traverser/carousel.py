# This file exists within 'dob-viewer':
#
#   https://github.com/hotoffthehamster/dob-viewer
#
# Copyright © 2019-2020 Landon Bouma. All rights reserved.
#
# This program is free software:  you can redistribute it  and/or  modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3  of the License,  or  (at your option)  any later version  (GPLv3+).
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY;  without even the implied warranty of MERCHANTABILITY or  FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU  General  Public  License  for  more  details.
#
# If you lost the GNU General Public License that ships with this software
# repository (read the 'LICENSE' file), see <http://www.gnu.org/licenses/>.

"""Facts Carousel"""

from gettext import gettext as _

import asyncio
import time

# (lb): We're using Click only for get_terminal_size. (The
#  UI and user interaction is otherwise all handled by PPT).
# MAYBE/2019-12-05: (lb): Decouple dob-viewer from click, used only for term. size.
import click_hotoffthehamster as click  # merely for get_terminal_size.

from inflector import English, Inflector

from nark.helpers.dev.profiling import profile_elapsed

from dob_viewer.ptkui.re_confirm import confirm

from ..crud.interrogate import ask_user_for_edits
from ..ptkui.dialog_overlay import show_message
from .action_manager import ActionManager
from .edits_manager import EditsManager
from .exceptions import catch_action_exception
from .styling_config import StylingConfig
from .update_handler import UpdateHandler
from .various_styles import color as styling_color
from .zone_content import ZoneContent
from .zone_manager import ZoneManager

__all__ = (
    'Carousel',
)


class Carousel(object):
    """"""
    def __init__(
        self,
        controller,
        edit_facts,
        orig_facts,
        dirty_callback,
        dry,
        content_lexer=None,  # Lexer() instance, used by ZoneContent.
        classes_style=None,  # Style dict, used by all the zone_*.py.
        matches_style=None,  # Matching logic and container-class map.
        no_completion=None,  # act/cat/tag list to not complete/suggest.
    ):
        self.controller = controller
        self.edits_manager = EditsManager(
            controller,
            edit_facts=edit_facts,
            orig_facts=orig_facts,
            dirty_callback=dirty_callback,
            error_callback=self.error_callback,
        )
        self.dry = dry
        self.content_lexer = content_lexer
        self.setup_styling(classes_style, matches_style)
        self.no_completion = no_completion
        self.action_manager = ActionManager(self)
        self.update_handler = UpdateHandler(self)
        # We'll set up the ZoneManager each time we use the event_loop.
        self.zone_manager = None
        self._avail_width = None
        self.setup_async()

    # ***

    @property
    def carousel(self):
        """Magic for reset_showing_help."""
        return self

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
        if not self.classes_style['content-width']:
            return full_width
        avail_width = min(self.classes_style['content-width'], full_width)
        return avail_width

    # ***

    def setup_async(self):
        # 2019-01-25: (lb): We run asynchronously to support such features as
        # tick_tock_now, which keeps the active fact's end clock time updated.
        # However, working with asyncio can be somewhat tricky. So, should you
        # need to disable it, here's a switch.
        # 2020-01-28: PTK3 is always-async, FYI.
        # - But we still need to be able to disable asyncio for tests.
        self._async_enable = True
        self._confirm_exit = False

    @property
    def async_enable(self):
        assert(self._async_enable)  # 2020-02-01: Always True now because PTK3.
        return self._async_enable

    @property
    def confirm_exit(self):
        return self._confirm_exit

    @confirm_exit.setter
    def confirm_exit(self, confirm_exit):
        self._confirm_exit = confirm_exit

    # ***

    def setup_styling(self, classes_style, matches_style):
        """"""

        def _setup_styling():
            setup_classes_style(classes_style)
            setup_matches_style(matches_style)

        def setup_classes_style(classes_style):
            if classes_style is None:
                # HARDCODED/DEFAULT: classes_style default: 'color'.
                # (lb): The styling_color() method (an alias of various_style.color())
                # qualifies as a *hardcoded* value (e.g., we could instead call light()
                # or night()). But this is merely a fallback in case the user cleared
                # the setting in their configuration, and then for some reason our
                # load_classes_style() stopped fetching the default first. In fact,
                # per that last point, this code is technically unreachable!
                self.controller.affirm(False)  # Nawgunnhappen.
                classes_style = styling_color()
            self.classes_style = classes_style

        def setup_matches_style(matches_style):
            self.stylability = StylingConfig(matches_style)

        _setup_styling()

    def add_stylable_classes(self, ppt_widget, friendly_name, fact=None):
        """Apply custom user classes from ~/.config/dob/styling/styles|stylit.conf
        to, e.g., use custom color backgrounds for Facts with matching Category."""
        fact = fact or self.carousel.edits_manager.curr_edit
        return self.stylability.add_stylable_classes(ppt_widget, friendly_name, fact)

    # ***

    def gallop(self, **kwargs):
        self.standup_once()
        if self.async_enable:
            # Get the OS thread's event loop.
            self.event_loop = asyncio.get_event_loop()
        confirmed_facts = self.run_edit_loop(**kwargs)

        # (lb): We did not start the event loop, so we should not stop it, e.g.,:
        #     self.async_enable and self.event_loop and self.event_loop.stop()
        # which I mention only because I generally like to clean up after myself.
        # (Nonetheless, it's harmless if the application is exiting anyway.
        #  It merely sets a boolean: `event_loop._stopping = True`.)

        # CLOSED_LOOP: (lb): Remember duration until self.event_loop.close()
        # called. At least until we figure out how to wait() to avoid kludge.
        #
        # FIXME/2019-01-27: Disable close_countdown and find better solution.
        # (And leaving this code-comment until that solution is discovered.)
        #
        #     if self.async_enable:
        #         self.close_countdown = time.time()

        return self.edits_manager.prepared_facts if confirmed_facts else []

    def whoa_nellie(self):
        """"""
        # CLOSED_LOOP: (lb): If we do not clean up properly (or fake it, and
        # drag our feet after quitting the Carousel, but before exiting app),
        # you might experience a RuntimeError such as:
        #
        #     Exception in thread Thread-12:
        #     Traceback (most recent call last):
        #       File "/usr/lib/python3.6/threading.py", line 916,
        #         in _bootstrap_inner
        #           self.run()
        #       ...
        #       File "/usr/lib/python3.6/asyncio/base_events.py", line 366,
        #         in _check_closed
        #           raise RuntimeError('Event loop is closed')
        #     RuntimeError: Event loop is closed
        #
        # 2019-01-27: I think this is reproducible on a large dob-import, after
        # pressing <Ctrl-s> to exit the Carousel and beginning persisting Facts.
        #
        # My first guess was the tick-tock task, but there are 5 threads' stack
        # traces (like the example reprinted above) printed to the terminal.
        # So maybe PPT has some other input processing or what not going on.
        #
        # (Also, note that we bounce around between 3 different uses of PPT,
        # stopping one to start another. 2 uses of PPT -- editing the act@gory
        # and editing tags -- are run without the event loop, whereas the other
        # use, running the Carousel, uses the event loop. There could be some
        # clean up or waiting not happening between uses.)
        #
        # I tried calling other functions (based on suggestions I found online), e.g.,
        #
        #     self.event_loop.run_until_complete(very_long_coroutine())
        #     ...
        #     self.event_loop.stop()
        #     self.event_loop.run_forever()
        #     self.event_loop.close()
        #
        # but none of that helped.
        #
        # (lb): I've seen the error with a ½ sec. wait; but never with 1 second.
        #   But there's no way I'm imposing 1 sec. wait. We'll find another way.
        #
        #   NAH:
        #
        #     wait_at_least_secs = 1.0
        #     remaining = wait_at_least_secs - (time.time() - self.close_countdown)
        #     if remaining > 0:
        #         time.sleep(remaining)
        #         pass

    @property
    def prepared_facts(self):
        return self.edits_manager.prepared_facts

    # ***

    def run_edit_loop(self, **kwargs):
        confirmed_facts = False
        used_prompt = None
        self.enduring_edit = True
        while self.enduring_edit:
            self.runloop(**kwargs)
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

            # CPR_ISSUE: An ever-so-brief pause after editing, before returning
            # to the Carousel, apparently precludes the Cursor Position Request
            # problem (which is documented in a comment in runloop_async).
            # 2019-01-27: (lb): I added this sleep before I added standup_always.
            #   MAYBE/2019-01-27: (lb): TEST: Determine if this sleep still
            #   necessary. Or just leave it, it's painless.
            if self.enduring_edit:
                time.sleep(0.01)

        return confirmed_facts

    def process_exit_request(self):
        if not self.edits_manager.is_dirty:
            # No Facts edited.
            return True
        question = _('\nReally exit without saving?')
        try:
            confirmed = confirm(question, erase_when_done=True)
        except KeyboardInterrupt:
            confirmed = True  # Eh?
        return confirmed

    def process_save_early(self):
        question = _('\nReally save without verifying all Facts?')
        confirmed = confirm(question, erase_when_done=True)
        return confirmed

    def prompt_fact_edits(self, used_prompt):
        try:
            used_prompt = self.user_prompt_edit_fact(used_prompt)
        except KeyboardInterrupt:
            # Ye olde Ctrl-c, and not an Exception.
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
            no_completion=self.no_completion,
        )
        return used_prompt

    # ***

    def standup_once(self):
        self.edits_manager.stand_up()

    def standup_always(self, **kwargs):
        self.zone_manager = ZoneManager(self)
        self.zone_manager.standup()
        self.action_manager.standup()
        self.update_handler.standup()
        self.action_manager.finalize_standup()  # Prints key binding errors.
        self.zone_manager.build_and_show(**kwargs)

    # ***

    def runloop(self, **kwargs):
        self.confirm_exit = False
        # Use enduring_edit as a trinary to know if the Carousel's run-loop
        # completes unexpectedly (it'll be None), or if the user interacted
        # with the application and it exited its loop deliberately (it'll be
        # True or False).
        self.enduring_edit = None
        self.restrict_edit = ''
        rerun_cnt = 0
        keep_running = True
        # MAGIC_NUMBER: CPR_ISSUE: Do not rerun > once, lest stuck in feedback loop.
        while keep_running and rerun_cnt < 2:
            keep_running = self.runloop_run(**kwargs)
            rerun_cnt += 1

    def runloop_run(self, **kwargs):
        profile_elapsed('To dob runloop')

        # CPR_ISSUE: (lb): 2019-01-27: This might be the Ultimate Fix, by which
        # I mean I added this code last, and it might all that's needed to get
        # around the CPR issue (in which case, the `enduring_edit is None`
        # kludge below may be unnecessary).
        self.standup_always(**kwargs)

        if self.async_enable:
            rerun = self.runloop_async()
            return rerun
        else:
            assert(False)  # 2020-02-01: Dead path now because always async.
            self.zone_manager.application.run()
            return False

    def runloop_async(self):
        # CPR_ISSUE: (lb): A Funky Business upon Rerunning Carousel.
        #
        # After the user edits the description, or the act@gory, or tags, the
        # application returns to the Carousel. But sometimes the Carousel
        # completes immediately. Then our code, not seeing enduring_edit,
        # exits, though the user was expecting to see the Carousel again.
        #
        # The user also sees what looks like CPR (cursor position request)
        # input on the terminal, for instance,
        #
        #     ^[[12;1R>
        #
        # I cannot deterministically reproduce the behavior other than to
        # cycle between the Carousel and editing, mashing keys to jump
        # quickly between states, and occasionally saving.
        #
        # We can kludge around the behavior by rerunning the Carousel if
        # it completely quickly (i.e., in less time then then use could have
        # interacted with it). (Though this introduces additional pitfalls,
        # like falling into an infinite feedback loop. Just be careful!)
        rerun = False

        # 2020-03-31: (lb): In earlier PTK, calling run_async() would draw the
        # app, but not run its event loop (so some Carousel code would run).
        # But now, this is truly async and nothing is invoked, just a coroutine
        # is returned.
        run_async = self.zone_manager.application.run_async()

        # Create the tick-tock task.
        # MAYBE/2020-01-30: See (new?) in PTK3: create_background_task.
        # - Maybe have PTK3 manage tick-tock, not us. (This works fine, though).
        tck_task = self.event_loop.create_task(self.tick_tock_now())

        # Leave tck_task out of tasks and manage separately.
        tasks = [run_async, ]

        # Run the Carousel!
        self.event_loop.run_until_complete(asyncio.wait(tasks))

        # Check if the Carousel exited deliberately or not.
        if self.enduring_edit is None:
            # CPR_ISSUE: (lb): Look in PPT for ask_for_cpr: this sends the CPR:
            #   Query Cursor Position: <ESC>[6n
            # The other junk you see on the terminal are cursor positions:
            #   Report Cursor Position: <ESC>[{ROW};{COLUMN}R
            # If code gets stuck in a loop, the request acts like Schrödinger's
            # cat and changes value each time it prints to the terminal, e.g.,
            #   ^[[11;1R^[[11;9R^[[11;17R^[[11;26R^[[11;35R
            #           ^[[12;9R^[[12;17R^...
            # (In other cases, you might see `;226R;226R;226R...` instead).
            # Ref:
            #   prompt_toolkit/renderer.py
            #       request_absolute_cursor_position
            self.controller.client_logger.warning('KLUDGE! Re-running Carousel.')
            rerun = True

        tck_task.cancel()
        # Similar to `await tck_task`, but this method not async function, so
        # go through the event loop. -In past, (lb)'s seen warning if skipped:
        #   RuntimeWarning: coroutine 'wait' was never    awaited
        self.event_loop.run_until_complete(asyncio.wait([tck_task, ]))

        return rerun

    # ***

    async def tick_tock_now(self):
        """"""
        async def _tick_tock_now():
            tocking = True
            while tocking:
                tocking = await tick_tock_loop()

        async def tick_tock_loop():
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
    def exit_command(self, event):
        """"""
        self.confirm_exit = True
        self.enduring_edit = False
        event.app.exit()

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def exit_quietly(self, event):
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
    def save_edited_and_exit(self, event):
        self.save_edited_and_live(event)
        # (lb): Exit Carousel, then Save. Traditional Import behavior
        # (before running save/save_edited_and_live was implemented).
        self.enduring_edit = False
        event.app.exit()
        return

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def save_edited_and_live(self, event):
        """"""
        # MAYBE/TESTME/2019-02-01: (lb): If running save on dob-import, use progger?
        # - Import save can take a while (because checks for conflicts on each Fact)
        #   -- do we need a Carousel progress display (progger)?
        curr_fact, saved_facts = self.edits_manager.save_edited_facts()
        if saved_facts is None:
            # Indicates error during save, and error message was displayed.
            return
        if not saved_facts:
            curr_fact = None
        if saved_facts:
            self.controller.post_process(
                self.controller,
                saved_facts,
                show_plugin_error=self.show_plugin_error,
                carousel_active=True,
            )
        edit_cnt = len(saved_facts)
        self.zone_manager.finalize_jump(
            curr_fact,
            noop_msg=_('Nothing to save'),
            jump_msg=_('Saved {} {}'.format(
                edit_cnt,
                Inflector(English).conditional_plural(edit_cnt, 'fact'),
            )),
        )

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
        if not self.controller.config['dev.catch_errors']:
            self.controller.client_logger.warning(
                _('Please enable ‘dev.catch_errors’ to use live debugging.')
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

