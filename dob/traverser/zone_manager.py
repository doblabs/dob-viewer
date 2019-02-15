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
"""Zone Manager"""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import click  # merely for get_terminal_size.

# Profiling: load prompt_toolkit: ~ 0.040 secs.
from prompt_toolkit.application import Application
from prompt_toolkit.layout.containers import (
    FloatContainer, HSplit, HorizontalAlign, VSplit
)
from prompt_toolkit.layout import Layout
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Box, Label


from . import various_styles
from .dialog_overlay import alert_and_question
from ..helpers.facts_diff import FactsDiff
from .zone_content import ZoneContent
from .zone_details import ZoneDetails
from .zone_epithet import ZoneEpithet
from .zone_lowdown import ZoneLowdown
from ..helpers.exceptions import catch_action_exception

__all__ = [
    'ZoneManager',
]


class ZoneManager(object):
    """"""
    def __init__(self, carousel):
        self.carousel = carousel
        self.facts_diff = None

        self.zone_epithet = ZoneEpithet(self.carousel)
        self.zone_details = ZoneDetails(self.carousel)
        self.zone_content = ZoneContent(self.carousel)
        self.zone_lowdown = ZoneLowdown(self.carousel)

        self.alert_showing = False
        self.silence_alert_overlapped = False

    # ***

    def standup(self):
        self.zone_epithet.standup()
        self.zone_details.standup()
        self.zone_content.standup()
        self.zone_lowdown.standup()

    # ***

    def build_and_show(self):
        self.root = self.build_root_container()
        self.layout = self.build_application_layout()
        self.setup_style()
        self.application = self.build_application_object()
        self.rebuild_viewable()

    # ***

    def build_root_container(self):
        self.epithet_posit = 0
        self.details_posit = 1
        self.content_posit = 2
        self.lowdown_posit = 3
        self.hsplit = HSplit(
            # Use placeholders; we'll populate in rebuild_containers().
            children=[
                Label(text=''),  # zone_epithet
                Label(text=''),  # zone_details
                Label(text=''),  # zone_content
                Label(text=''),  # zone_lowdown
            ],
            # There can be top-bottom padding, e.g.,:
            #  padding=3,
            #  padding_char='X',
            #  padding_style='',
        )

        if self.carousel.chosen_style['root-app_align'] == 'JUSTIFY':
            app_align = HorizontalAlign.JUSTIFY
            app_width = None
        else:
            app_align = HorizontalAlign.LEFT
            app_width = click.get_terminal_size()[0]

        self.vsplit = VSplit(
            [self.hsplit],
            align=app_align,
            width=app_width,
        )

        root_container = FloatContainer(Box(body=self.vsplit), floats=[])
        return root_container

    def build_application_layout(self):
        layout = Layout(
            container=self.root,
            # Will get set later:
            #   focused_element
            # EXPLAIN/2019-01-21: How does focused_element get set?
            #  Automatically? Side effect of another call?
            #  The Layout() constructor has a focused_element attr,
            #   but we do not need to set it.
        )
        return layout

    def setup_style(self):
        if self.carousel.chosen_style is None:
            self.carousel.chosen_style = various_styles.color()
        self.style = Style(self.carousel.chosen_style['container-syles'])

    def build_application_object(self):
        # (lb): By default, the app uses editing_mode=EditingMode.EMACS,
        # which adds a few key bindings. One binding in particular is a
        # little annoying -- ('c-x', 'c-x') -- because PPT has to wait
        # for a second key press, or a timeout, to resolve the binding.
        # E.g., if you press 'c-x', it takes a sec. until our handler is
        # called (or, it's called if you press another key, but then the
        # response seems weird, i.e., 2 key presses are handle seemingly
        # simultaneously after the second keypress, rather than being
        # handled individually as the user presses them keys). In any
        # case -- long comment! -- set editing_mode to something other
        # than EditingMode.EMACS or EditingMode.VI (both are just strings).

        application = Application(
            layout=self.layout,
            key_bindings=self.carousel.action_manager.key_bindings_normal,
            full_screen=False,
            erase_when_done=True,
            # Enables mouse wheel scrolling.
            # CAVEAT: Steals from terminal app!
            #   E.g., while app is active, mouse wheel scrolling no
            #   longer scrolls the desktop Terminal app window, ha!
            # FIXME: Make this feature optionable. Seems like some
            #   people may appreciate this wiring.
            mouse_support=True,
            style=self.style,
            # The scrollable content area disables input with
            #   read_only=True
            # which we could do here by disabling built-in buffer
            # editing bindings, i.e.,
            #   editing_mode='',
            # but we want those bindings for the command inputizer.
        )
        return application

    # ***

    def rebuild_viewable(self):
        """
        rebuild_viewable is called to update the view after the user edits a
        fact or navigates to a different fact.

        HINT: If the view gets messed up, say by a pdb session, this function
        will not redraw everything. See instead:

            self.application.renderer.clear()
        """
        self.reset_diff_fact()
        self.rebuild_containers()
        self.assemble_focus_jumps()
        self.selectively_refresh()
        self.carousel.controller.client_logger.debug(_('rebuilt and refreshed'))

    def reset_diff_fact(self):
        orig_fact = self.carousel.edits_manager.curr_orig
        # Call editable_fact, which either gets the edit_fact, or gets
        # a copy of the orig_fact; but it does not make an undo.
        edit_fact = self.carousel.edits_manager.editable_fact()
        self.facts_diff = FactsDiff(orig_fact, edit_fact, formatted=True)
        self.carousel.controller.client_logger.debug(
            'facts_diff: {}'.format(self.facts_diff),
        )

    def rebuild_containers(self):
        epithet_container = self.zone_epithet.rebuild_viewable()
        self.hsplit.get_children()[self.epithet_posit] = epithet_container

        details_container = self.zone_details.rebuild_viewable()
        self.hsplit.get_children()[self.details_posit] = details_container

        content_container = self.zone_content.rebuild_viewable()
        self.hsplit.get_children()[self.content_posit] = content_container

        lowdown_container = self.zone_lowdown.rebuild_viewable()
        self.hsplit.get_children()[self.lowdown_posit] = lowdown_container

    # ***

    def selectively_refresh(self):
        self.zone_epithet.selectively_refresh()
        self.zone_details.selectively_refresh()
        self.zone_content.selectively_refresh()
        self.zone_lowdown.selectively_refresh()

    # ***

    def assemble_focus_jumps(self):
        content_control = self.content_control
        start_control = self.widget_control_time_start
        end_control = self.widget_control_time_end

        self.focus_chain = [
            content_control,
            start_control,
            end_control,
        ]

        self.focus_surround = {
            content_control: self.zone_content.focus_content,
            start_control: self.zone_details.edit_time_start,
            end_control: self.zone_details.edit_time_end,
        }

        self.focus_recent = content_control

    @catch_action_exception
    def focus_next(self, event):
        # Note also:
        #   prompt_toolkit.key_binding.bindings.focus.focus_next
        self.focus_move(lambda index: (index + 1) % len(self.focus_chain))

    @catch_action_exception
    def focus_previous(self, event):
        # Note also:
        #   prompt_toolkit.key_binding.bindings.focus.focus_previous
        self.focus_move(lambda index: (index or len(self.focus_chain)) - 1)

    def focus_move(self, index_f):
        # NOTE: PPT has focus_next(event), which can cycle through focusable
        #       containers, but the edit-time controls are on-demand, so we
        #       do this manually.
        curr_control = self.layout.current_control
        defocused = self.focus_surround[curr_control](focus=False)
        if not defocused:
            return
        curr_index = self.focus_chain.index(curr_control)
        curr_index = self.focus_index(curr_control)
        next_index = index_f(curr_index)
        next_control = self.focus_chain[next_index]
        self.focus_surround[next_control](focus=True)
        self.focus_recent = curr_control

    def focus_index(self, which_control=None):
        if which_control is None:
            which_control = self.layout.current_control
        which_index = self.focus_chain.index(which_control)
        return which_index

    @property
    def content_control(self):
        return self.zone_content.content.control

    @property
    def widget_control_time_end(self):
        return self.zone_details.widgets_end.text_area.control

    @property
    def widget_control_time_start(self):
        return self.zone_details.widgets_start.text_area.control

    # ***

    @catch_action_exception
    # SKIP: @ZoneContent.Decorators.reset_showing_help
    def toggle_focus_time_end(self, event):
        self.toggle_focus_time(self.widget_control_time_end)

    @catch_action_exception
    # SKIP: @ZoneContent.Decorators.reset_showing_help
    def toggle_focus_time_start(self, event):
        self.toggle_focus_time(self.widget_control_time_start)

    def toggle_focus_time(self, time_control):
        focus = self.layout.current_control is not time_control
        if focus:
            which_index = self.focus_index(time_control)
        else:
            # (lb): Toggling to recent sorta feels weird.
            #   which_index = self.focus_index(self.focus_recent)
            # Toggling between content and time feels more natural.
            which_index = self.focus_index(self.content_control)
        self.focus_move(lambda index: which_index)

    # ***

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def jump_fact_dec(self, event):
        """"""
        prev_fact = self.carousel.edits_manager.jump_fact_dec()
        self.finalize_jump_dec(prev_fact)

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def jump_fact_inc(self, event):
        """"""
        next_fact = self.carousel.edits_manager.jump_fact_inc()
        self.finalize_jump_inc(next_fact)

    # ***

    # (lb): NOTE/2019-01-24: There are no explicit jump-week or jump-month,
    # etc., commands, but if the user keeps the 'J' or 'K' keys pressed
    # (the prev and next day commands) for an extended length of time, the
    # Carousel will start jumping by larger time increments.

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def jump_day_dec(self, event):
        """"""
        prev_fact = self.carousel.edits_manager.jump_day_dec()
        self.finalize_jump_dec(prev_fact)

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def jump_day_inc(self, event):
        """"""
        next_fact = self.carousel.edits_manager.jump_day_inc()
        self.finalize_jump_inc(next_fact)

    # ***

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def jump_rift_dec(self, event):
        """"""
        was_curr = self.carousel.edits_manager.curr_fact
        self.carousel.edits_manager.jump_rift_dec()
        self.refresh_fact_or_notify_noop(was_curr, _("Already on first Fact"))

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def jump_rift_inc(self, event):
        """"""
        was_curr = self.carousel.edits_manager.curr_fact
        self.carousel.edits_manager.jump_rift_inc()
        self.refresh_fact_or_notify_noop(was_curr, _("Already on final Fact"))

    def refresh_fact_or_notify_noop(self, was_curr, noop_msg):
        if was_curr is not self.carousel.edits_manager.curr_fact:
            self.rebuild_viewable()
        else:
            self.update_status(noop_msg)

    # ***

    def finalize_jump_dec(self, prev_fact):
        """"""
        self.finalize_jump_check_overlapped(
            prev_fact, noop_msg=_("Viewing earliest Fact"),
        )

    def finalize_jump_inc(self, next_fact):
        """"""
        self.finalize_jump_check_overlapped(
            next_fact, noop_msg=_("Viewing latest Fact"),
        )

    def finalize_jump_check_overlapped(self, curr_fact, noop_msg):
        def _finalize_jump_check_overlapped():
            jump_msg = ''
            if curr_fact and 'alert-user' in curr_fact.dirty_reasons:
                curr_fact.dirty_reasons.discard('alert-user')
                # 2019-02-13: (lb): Currently, only 'overlapped' causes this.
                self.carousel.controller.affirm(
                    curr_fact.dirty_reasons == set(['overlapped']),
                )
                popop_modal_alert_overlapped_fact()
                jump_msg = _('ALERT! Corrected overlapping Fact times. Save to commit.')
            self.finalize_jump(curr_fact, noop_msg, jump_msg)

        def popop_modal_alert_overlapped_fact():
            if self.silence_alert_overlapped:
                return
            alert_and_question(
                self.root,
                title=_('Overlapping Fact'),
                label_text=_(
                    'A Fact loaded from the data store overlaps an adjacent Fact.'
                ) + '\n\n' + _(
                    'The Fact has been updated and is staged to be saved.'
                ),
                prompt_ok=_('Got it!'),
                prompt_no=_('Keep reminding me'),
                on_close=self.on_alert_overlapped_close,
            )
            # Disable any input recognize (let PPT's dialog handle everything).
            self.carousel.action_manager.wire_keys_modal()

        _finalize_jump_check_overlapped()

    def on_alert_overlapped_close(self, result):
        self.alert_showing = False
        if result:
            self.silence_alert_overlapped = True
        # Re-enable keyboard input processing.
        self.carousel.action_manager.wire_keys_normal()

    def finalize_jump(self, curr_fact, noop_msg, jump_msg=''):
        if curr_fact is None:
            self.update_status(noop_msg)
        else:
            self.zone_content.reset_cursor_left_column()
            self.rebuild_viewable()
            if jump_msg:
                self.update_status(jump_msg)

    # ***

    def update_status(self, hot_notif):
        self.zone_lowdown.update_status(hot_notif)

