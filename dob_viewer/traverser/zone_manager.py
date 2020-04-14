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

"""Zone Manager"""

from gettext import gettext as _

import os
from inflector import English, Inflector

# MAYBE/2019-12-05: (lb): Decouple dob-viewer from click, used only for term. size.
import click_hotoffthehamster as click  # merely for get_terminal_size.

# Profiling: load prompt_toolkit. ~ 0.040 secs.
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import (
    FloatContainer,
    HorizontalAlign,
    HSplit,
    VSplit
)
from prompt_toolkit.output.color_depth import ColorDepth
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Box, Label

from ..crud.facts_diff import FactsDiff
from ..ptkui.dialog_overlay import alert_and_question
from .exceptions import catch_action_exception
from .zone_content import ZoneContent
from .zone_details import ZoneDetails
from .zone_lowdown import ZoneLowdown
from .zone_streamer import ZoneStreamer

__all__ = (
    'ZoneManager',
)


class ZoneManager(object):
    """"""
    def __init__(self, carousel):
        self.carousel = carousel
        self.facts_diff = None

        self.zone_streamer = ZoneStreamer(self.carousel)
        self.zone_details = ZoneDetails(self.carousel)
        self.zone_content = ZoneContent(self.carousel)
        self.zone_lowdown = ZoneLowdown(self.carousel)

        self.alert_showing = False
        self.silence_alert_overlapped = False

    # ***

    def standup(self):
        self.zone_streamer.standup()
        self.zone_details.standup()
        self.zone_content.standup()
        self.zone_lowdown.standup()
        self.assemble_focus_jumps()

    # ***

    def build_and_show(self, **kwargs):
        self.root = self.build_root_container()
        self.layout = self.build_application_layout()
        self.setup_styling()
        self.application = self.build_application_object(**kwargs)
        self.rebuild_viewable()

    # ***

    def build_root_container(self):
        self.streamer_posit = 0
        self.details_posit = 1
        self.content_posit = 2
        self.lowdown_posit = 3
        self.hsplit = HSplit(
            # Use placeholders; we'll populate in rebuild_containers().
            children=[
                Label(text=''),  # zone_streamer
                Label(text=''),  # zone_details
                Label(text=''),  # zone_content
                Label(text=''),  # zone_lowdown
            ],
            # There can be top-bottom padding, e.g.,:
            #  padding=3,
            #  padding_char='X',
            #  padding_style='',
        )

        if self.carousel.classes_style['editor-align'] == 'LEFT':
            app_align = HorizontalAlign.LEFT
            app_width = click.get_terminal_size()[0]
        elif self.carousel.classes_style['editor-align'] == 'CENTER':
            app_align = HorizontalAlign.CENTER
            app_width = None
        elif self.carousel.classes_style['editor-align'] == 'RIGHT':
            app_align = HorizontalAlign.RIGHT
            app_width = click.get_terminal_size()[0]
        else:
            # self.carousel.classes_style['editor-align'] == 'JUSTIFY'
            app_align = HorizontalAlign.JUSTIFY
            app_width = None

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

    def setup_styling(self):
        class_styles = self.carousel.classes_style['collect_tups']
        try:
            self.style = Style(class_styles)
        except Exception as err:
            # FIXME: Show error in Carousel, or raise and show before first draw.
            #        - You could show error on startup, pause for input,
            #        then continue (could even decide not to show warning again?).
            # FIXME: Find all controller usage from clyde and refactor so has to
            #        be passed in (wire what you need from dob upfront).
            from dob_bright.termio import dob_in_user_warning
            msg = _('The user style “{0}” failed to load: {1}').format(
                self.carousel.controller.config['editor.styling'], str(err),
            )
            self.carousel.controller.client_logger.warning(msg)
            dob_in_user_warning(str(class_styles))
            dob_in_user_warning(msg)
            self.style = Style([])

    def _detect_color_depth(self):
        # MAYBE/2020-01-06: Make color_depth configurable. Or detect better.
        # (lb): This is a little frustrating. Colors are true in mate-terminal, but
        #   in tmux, they're being "rounded", e.g., my custom class:category-sleep,
        #   which is #CA85AC pink, is being rounded to straight up 0xFF0000 red.
        #   - I have TERM=xterm in both cases (albeit not advisable in tmux, it's
        #     the only TERM I can get italics to work in). And when I trace code
        #     here, it seems like TERM defaults to DEPTH_8_BIT in either case --
        #     but for some reason, under tmux, there's color rounding.
        #   - One solution/work-around is to use ColorDepth.DEPTH_24_BIT when...
        #     unfortunately, I'm not sure the best way to detect if the terminal
        #     supports truecolor. Obvi., for me, I'll always have a truecolor
        #     terminal at my fingers, or will fix it if I don't but for other
        #     users, I want to ensure they have a decent experience always.
        #     - We can check COLORTERM, which I think is set by mate-terminal,
        #       except when I searched the source, I did not see it therein.
        #       But works for me! (I mean, we could just always set 24-bit color,
        #       but this at least falls back to not doing anything if COLORTERM is
        #       not set as expected, which seems like the safest course of action.)
        # Default, which works in raw mate-terminal, but not under tmux:
        #   color_depth=ColorDepth.DEPTH_8_BIT,
        if os.environ.get('COLORTERM', None) != 'truecolor':
            return None
        return ColorDepth.DEPTH_24_BIT

    def build_application_object(self, **kwargs):
        # (lb): By default, the app uses editing_mode=EditingMode.EMACS,
        # which adds a few key bindings. One binding in particular is a
        # little annoying -- ('c-x', 'c-x') -- because PPT has to wait
        # for a second key press, or a timeout, to resolve the binding.
        # E.g., if you press 'c-x', it takes a sec. until our handler is
        # called (or, it's called if you press another key, but then the
        # response seems weird, i.e., 2 key presses are handled seemingly
        # simultaneously after the second keypress, rather than being
        # handled individually as the user presses them keys). In any
        # case -- long comment! -- set editing_mode to something other
        # than EditingMode.EMACS or EditingMode.VI (both are just strings).
        # FIXME/2019-11-23: (lb): That comment is old, because we do not
        # disable editing_mode, but we leave it set to emacs for some
        # other features. Question is, is there a delay on Ctrl-x? And
        # what does Ctrl-X do? Is it meta-cut? Also, what are the emacs-
        # binding features that you like?
        application = Application(
            layout=self.layout,
            key_bindings=self.carousel.action_manager.key_bindings_normal,
            full_screen=False,
            color_depth=self._detect_color_depth(),
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
            **kwargs,
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
        streamer_container = self.zone_streamer.rebuild_viewable()
        self.hsplit.get_children()[self.streamer_posit] = streamer_container

        details_container = self.zone_details.rebuild_viewable()
        self.hsplit.get_children()[self.details_posit] = details_container

        content_container = self.zone_content.rebuild_viewable()
        self.hsplit.get_children()[self.content_posit] = content_container

        lowdown_container = self.zone_lowdown.rebuild_viewable()
        self.hsplit.get_children()[self.lowdown_posit] = lowdown_container

    # ***

    def selectively_refresh(self):
        self.zone_streamer.selectively_refresh()
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
        # NOTE: PTK has focus_next(event), which can cycle through focusable
        #       containers, but the edit-time controls are on-demand, so we
        #       do this manually.
        curr_control = self.layout.current_control
        try:
            defocused = self.focus_surround[curr_control](focus=False)
        except Exception as err:  # noqa: F841 local variable ... never used
            # 2020-04-07: See d4d12cc3. This should be fixed!
            self.carousel.controller.affirm(False)  # REPL if dev.catch_errors.
            return
        if not defocused:
            return
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
        self.toggle_focus_time_widget(self.widget_control_time_end)

    @catch_action_exception
    # SKIP: @ZoneContent.Decorators.reset_showing_help
    def toggle_focus_time_start(self, event):
        self.toggle_focus_time_widget(self.widget_control_time_start)

    def toggle_focus_time_widget(self, time_control):
        focus = self.layout.current_control is not time_control
        if focus:
            which_index = self.focus_index(time_control)
        else:
            # (lb): Toggling to recent sorta feels weird.
            #   which_index = self.focus_index(self.focus_recent)
            # Toggling between content and time feels more natural.
            which_index = self.focus_index(self.content_control)
        self.focus_move(lambda index: which_index)

    def ppt_control_buffer_avoid_selection(self, control, mouse_event):
        # python-prompt-toolkit/prompt_toolkit/layout/controls.py's
        # BufferControl.mouse_handler
        # on MouseEventType.MOUSE_UP
        # calls buffer.start_selection
        # if user clicks anywhere except the cursor_position,
        # so ensure the cursor_position is set on MOUSE_DOWN
        # to the click, otherwise the MOUSE_UP that is about
        # to happen will create an awkward selection in the
        # widget.
        buffer = control.buffer
        index = buffer.document.translate_row_col_to_index(
            mouse_event.position.y, mouse_event.position.x,
        )
        buffer.exit_selection()
        buffer.cursor_position = index

    # ***

    def jump_msg_with_count(self, count, direction, what):
        return '{} {} {}'.format(
            direction,
            count,
            Inflector(English).conditional_plural(count, what),
        )

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def jump_fact_dec(self, event):
        """"""
        count = self.carousel.update_handler.apply_count_multiplier()
        jump_msg = self.jump_msg_with_count(count, _('Backward'), _('Fact'))
        prev_fact = self.carousel.edits_manager.jump_fact_dec(count=count)
        self.finalize_jump_dec(prev_fact, jump_msg)

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def jump_fact_inc(self, event):
        """"""
        count = self.carousel.update_handler.apply_count_multiplier()
        jump_msg = self.jump_msg_with_count(count, _('Forward'), _('Fact'))
        next_fact = self.carousel.edits_manager.jump_fact_inc(count=count)
        self.finalize_jump_inc(next_fact, jump_msg)

    # ***

    # (lb): NOTE/2019-01-24: There are no explicit jump-week or jump-month,
    # etc., commands, but if the user keeps the 'J' or 'K' keys pressed
    # (the prev and next day commands) for an extended length of time, the
    # Carousel will start jumping by larger time increments.

    def jump_msg_count_and_time(self, count, direction, what):
        return '{} ({} {})'.format(
            self.jump_msg_with_count(count, direction, what),
            _('from'),
            str(self.carousel.edits_manager.conjoined.jump_time_reference),
        )

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def jump_day_dec(self, event):
        """"""
        count = self.carousel.update_handler.apply_count_multiplier(floats=True)
        jump_msg = self.jump_msg_count_and_time(count, _('Backward'), _('Day'))
        prev_fact = self.carousel.edits_manager.jump_day_dec(days=count)
        self.finalize_jump_dec(prev_fact, jump_msg)

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def jump_day_inc(self, event):
        """"""
        count = self.carousel.update_handler.apply_count_multiplier(floats=True)
        jump_msg = self.jump_msg_count_and_time(count, _('Forward'), _('Day'))
        next_fact = self.carousel.edits_manager.jump_day_inc(days=count)
        self.finalize_jump_inc(next_fact, jump_msg)

    # ***

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def jump_rift_dec(self, event):
        """"""
        rift_jumper = self.carousel.edits_manager.jump_rift_dec
        noop_msg = _("Already on first Fact")
        self.jump_rift_or_time(rift_jumper, 'until_time', noop_msg)

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def jump_rift_inc(self, event):
        """"""
        rift_jumper = self.carousel.edits_manager.jump_rift_inc
        noop_msg = _("Already on final Fact")
        self.jump_rift_or_time(rift_jumper, 'since_time', noop_msg)

    def jump_rift_or_time(self, rift_jumper, which_time, noop_msg):
        was_curr = self.carousel.edits_manager.curr_fact
        modifier = self.carousel.update_handler.command_modifier
        self.carousel.update_handler.command_modifier_reset()
        if not modifier:
            rift_jumper()
        else:
            jump_time, parse_err = self.zone_details.parse_dated(modifier)
            if parse_err is not None:
                noop_msg = _("Not a time or date")
            else:
                facts_mgr = self.carousel.edits_manager.conjoined
                kwargs = {which_time: jump_time}
                facts_mgr.jump_to_fact_nearest(**kwargs)
                noop_msg = _("Nothing on that date")
        self.refresh_fact_or_notify_noop(was_curr, noop_msg)

    def refresh_fact_or_notify_noop(self, was_curr, noop_msg):
        if was_curr is not self.carousel.edits_manager.curr_fact:
            self.rebuild_viewable()
        else:
            self.update_status(noop_msg)

    # ***

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def jump_fact_first(self, event):
        """"""
        was_curr = self.carousel.edits_manager.curr_fact
        self.carousel.edits_manager.jump_fact_first()
        self.refresh_fact_or_notify_noop(was_curr, _("Already on first Fact"))

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def jump_fact_final(self, event):
        """"""
        was_curr = self.carousel.edits_manager.curr_fact
        self.carousel.edits_manager.jump_fact_final()
        self.refresh_fact_or_notify_noop(was_curr, _("Already on final Fact"))

    # ***

    def finalize_jump_dec(self, prev_fact, jump_msg):
        """"""
        self.finalize_jump_check_overlapped(
            prev_fact, noop_msg=_("Viewing earliest Fact"), jump_msg=jump_msg,
        )

    def finalize_jump_inc(self, next_fact, jump_msg):
        """"""
        self.finalize_jump_check_overlapped(
            next_fact, noop_msg=_("Viewing latest Fact"), jump_msg=jump_msg,
        )

    def finalize_jump_check_overlapped(self, curr_fact, noop_msg, jump_msg=''):
        def _finalize_jump_check_overlapped():
            _jump_msg = jump_msg
            if curr_fact and 'alert-user' in curr_fact.dirty_reasons:
                curr_fact.dirty_reasons.discard('alert-user')
                # 2019-02-13: (lb): Currently, only 'overlapped' causes this.
                self.carousel.controller.affirm(
                    curr_fact.dirty_reasons == set(['overlapped']),
                )
                popop_modal_alert_overlapped_fact()
                _jump_msg = _('ALERT! Corrected overlapping Fact times. Save to commit.')
            self.finalize_jump(curr_fact, noop_msg, _jump_msg)

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

