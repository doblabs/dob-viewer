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

"""Key Binding Action Handler Shim"""

from functools import update_wrapper

__all__ = (
    'KeyActionMap',
)


class KeyActionMap(object):
    """"""
    def __init__(self, carousel):
        self.carousel = carousel

        self.zone_manager = carousel.zone_manager

        self.zone_content = carousel.zone_manager.zone_content
        self.zone_details = carousel.zone_manager.zone_details
        self.zone_lowdown = carousel.zone_manager.zone_lowdown

        self.update_handler = carousel.update_handler

    # ***

    class Decorators(object):
        @classmethod
        def debug_log_trace_enter_leave(cls, func):
            def trace_enter_leave_wrapper(obj, event, *args, **kwargs):
                # 2019-01-17: [lb]: I added this wrapper to help delimit debug
                # trace messages (to determine where each command's messages
                # begin and end). But it might later be useful for other tasks,
                # such as profiling. So leaving here, but with a note that says,
                # yeah, this code has little utility to the end consumer, other
                # than to make the developer more comfortable in the code jungle.
                debug = obj.carousel.controller.client_logger.debug
                debug('🚿 🐎 ENTER 👋 🍩 “{}”'.format(func.__name__))
                func(obj, event, *args, **kwargs)
                # Include a visual delimiter to make it easy to scan log trace
                # and see groups of messages belonging to each command.
                debug('🍖 🛀 LEAVE 🐵 🍌 “{}”'.format(func.__name__))

            return update_wrapper(trace_enter_leave_wrapper, func)

        # ***

        @classmethod
        def refresh_now(cls, func):
            def wrapper(obj, event, *args, **kwargs):
                # So that we don't have to call controller.store.now_tz_aware()
                # in our handlers, and so our handlers do not have to worry that
                # "now" has different values during the event handling, reset now
                # now.
                obj.carousel.controller.now_refresh()
                func(obj, event, *args, **kwargs)

            return update_wrapper(wrapper, func)

        # ***

        @classmethod
        def intercept_modifier(cls, reset=False):
            """Passes key press to command modifier accumulator if necessary.

            Also resets the command modifier if indicatd by the command being
            decorated."""
            def _intercept_modifier(func):
                def wrapper(obj, event, *args, **kwargs):
                    command_modifier = obj.carousel.update_handler.command_modifier
                    re_date_seps = obj.carousel.update_handler.re_date_seps
                    # Check if '.' and pass to command modifier if started.
                    # - This enables a fractional command modifier to coexist
                    #   with a user command mapped to '.'. I.e., if no modifier
                    #   and user presses '.', execute the mapped command. But
                    #   if modifier started and '.', treat as decimal point.
                    if (
                        command_modifier
                        and (
                            (
                                event.data == '.'
                                # Can only be one '.' in modifier, so check not seen.
                                # (lb): This is somewhat awkward behavior, e.g., if
                                # user tries typing a date prefix (e.g., for the 'G'
                                # command) using periods, say, `2020.01.` on the
                                # second dot, it'll execute the '.' command. Oh well.
                                and '.' not in command_modifier
                            )
                            or (
                                # Note that date separators are allowed more than once,
                                # meaning any command mapped to a key also used as a
                                # date separator will be shadowed by this code and
                                # therefore cannot be called with a command modifier.
                                re_date_seps.match(event.data)
                            )
                        )
                    ):
                        obj.carousel.update_handler.command_modifier_any_key(event)
                    else:
                        if reset:
                            obj.carousel.update_handler.reset_time_multipliers()
                        func(obj, event, *args, **kwargs)

                return update_wrapper(wrapper, func)

            return _intercept_modifier

        # ***

    # #### Key bindings wired by KeyBonder.widget_focus().

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def focus_next(self, event):
        self.zone_manager.focus_next(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def focus_previous(self, event):
        self.zone_manager.focus_previous(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def edit_time_start(self, event):
        self.zone_manager.toggle_focus_time_start(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def edit_time_end(self, event):
        self.zone_manager.toggle_focus_time_end(event)

    # #### Key bindings wired by KeyBonder.save_and_quit().

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def save_edited_and_live(self, event):
        self.carousel.save_edited_and_live(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def save_edited_and_exit(self, event):
        self.carousel.save_edited_and_exit(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def exit_command(self, event):
        self.carousel.exit_command(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def exit_quietly(self, event):
        was_helping = self.zone_content.on_reset_hide_help()
        if was_helping:
            return
        self.carousel.exit_quietly(event)

    # #### Key bindings wired by KeyBonder.edit_time().

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def edit_time_enter(self, event):
        self.zone_details.edit_time_enter(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def toggle_focus_description(self, event):
        self.zone_details.toggle_focus_description(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def edit_time_any_key(self, event):
        self.zone_details.edit_time_any_key(event)

    # #### Key bindings wired by KeyBonder.undo_redo().

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def undo_command_content(self, event):
        self.update_handler.undo_command(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def redo_command_content(self, event):
        self.update_handler.redo_command(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def undo_command_edit_time(self, event):
        self.zone_details.undo_command(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def redo_command_edit_time(self, event):
        self.zone_details.redo_command(event)

    # #### Key bindings wired by KeyBonder.shortcuts().

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def copy_complete_and_paste_active(self, event):
        self.update_handler.copy_complete_and_paste_active(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def copy_complete_and_paste_new(self, event):
        self.update_handler.copy_complete_and_paste_new(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def complete_and_prompt_new(self, event):
        self.update_handler.complete_and_prompt_new(event)

    # #### Key bindings wired by KeyBonder.custom_factoids().

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def custom_factoid_paste(self, event):
        self.update_handler.custom_factoid_paste(event)

    # #### Key bindings wired by KeyBonder.normal().

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def rotate_help(self, event):
        self.zone_content.rotate_help(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def dev_breakpoint(self, event):
        self.carousel.dev_breakpoint(event)

    # *** Next/Prev: Fact

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def jump_fact_dec(self, event):
        self.zone_manager.jump_fact_dec(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def jump_fact_inc(self, event):
        try:
            self.zone_manager.jump_fact_inc(event)
        except Exception:
            # 2019-12-03 01:18: Raised on add-tag then save. Don't remember jumping.
            self.carousel.controller.affirm(False)
            pass

    # *** Next/Prev: Day

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def jump_day_dec(self, event):
        self.zone_manager.jump_day_dec(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def jump_day_inc(self, event):
        self.zone_manager.jump_day_inc(event)

    # *** Next/Prev: Rift

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def jump_rift_dec(self, event):
        self.zone_manager.jump_rift_dec(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def jump_rift_inc(self, event):
        self.zone_manager.jump_rift_inc(event)

    # *** First/Final: Fact

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def jump_fact_first(self, event):
        self.zone_manager.jump_fact_first(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def jump_fact_final(self, event):
        self.zone_manager.jump_fact_final(event)

    # *** Up/Down: Content Cursor Motion

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def cursor_up_one(self, event):
        self.zone_content.cursor_up_one(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def cursor_down_one(self, event):
        self.zone_content.cursor_down_one(event)

    # *** Up/Down/Top/Bottom: Content Scrolling

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def scroll_up(self, event):
        self.zone_content.scroll_up(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def scroll_down(self, event):
        self.zone_content.scroll_down(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def scroll_top(self, event):
        self.zone_content.scroll_top(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def scroll_bottom(self, event):
        self.zone_content.scroll_bottom(event)

    # #### Key bindings wired by KeyBonder.edit_fact().

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def edit_fact(self, event):
        self.update_handler.edit_fact(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def edit_actegory(self, event):
        self.update_handler.edit_actegory(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def edit_description(self, event):
        self.update_handler.edit_description(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def edit_tags(self, event):
        self.update_handler.edit_tags(event)

    # #### Key bindings wired by KeyBonder.nudge_time().

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def edit_time_decrement_start(self, event):
        self.update_handler.edit_time_decrement_start(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def edit_time_increment_start(self, event):
        self.update_handler.edit_time_increment_start(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def edit_time_decrement_end(self, event):
        self.update_handler.edit_time_decrement_end(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def edit_time_increment_end(self, event):
        self.update_handler.edit_time_increment_end(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def edit_time_decrement_both(self, event):
        self.update_handler.edit_time_decrement_both(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def edit_time_increment_both(self, event):
        self.update_handler.edit_time_increment_both(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def edit_time_decrement_start_5min(self, event):
        self.update_handler.edit_time_decrement_start_5min(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def edit_time_increment_start_5min(self, event):
        self.update_handler.edit_time_increment_start_5min(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def edit_time_decrement_end_5min(self, event):
        self.update_handler.edit_time_decrement_end_5min(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier()
    def edit_time_increment_end_5min(self, event):
        self.update_handler.edit_time_increment_end_5min(event)

    # #### Key bindings wired by KeyBonder.command_modifier().

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    def allow_time_gap(self, event):
        self.update_handler.allow_time_gap(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    # Not necessary: @Decorators.intercept_modifier()
    # (because gaits to the same handler anyway).
    def command_modifier_any_key(self, event):
        self.update_handler.command_modifier_any_key(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    # NOPE: @Decorators.intercept_modifier()
    def backspace_command_modifier(self, event):
        self.update_handler.backspace_command_modifier(event)

    # #### Key bindings wired by KeyBonder.create_delete_fact().

    # FIXME/2020-04-11: Remove these, or implement!

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def fact_split(self, event):
        self.update_handler.fact_split(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def fact_erase(self, event):
        self.update_handler.fact_erase(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def fact_merge_prev(self, event):
        self.update_handler.fact_merge_prev(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def fact_merge_next(self, event):
        self.update_handler.fact_merge_next(event)

    # #### Key bindings wired by KeyBonder.clipboard().

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def fact_copy_fact(self, event):
        self.update_handler.fact_copy_fact(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def fact_cut(self, event):
        self.update_handler.fact_cut(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def fact_paste(self, event):
        self.update_handler.fact_paste(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def fact_copy_activity(self, event):
        self.update_handler.fact_copy_activity(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def fact_copy_tags(self, event):
        self.update_handler.fact_copy_tags(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def fact_copy_description(self, event):
        self.update_handler.fact_copy_description(event)

    # #### Key bindings wired by KeyBonder.begin_commando().

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def begin_commando(self, event):
        self.update_handler.begin_commando(event)

    # #### Key bindings wired by KeyBonder.going_commando().

    # The following handlers occur after keybindings are rewired,
    # so there's no need to call the intercept decorator:
    #
    #   NOPE: @Decorators.intercept_modifier

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    def cancel_commando(self, event):
        self.update_handler.cancel_commando(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    def parts_commando(self, event):
        self.update_handler.parts_commando(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    def backspace_commando(self, event):
        self.update_handler.backspace_commando(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    def final_commando(self, event):
        self.update_handler.final_commando(event)

    # #### Key bindings wired by KeyBonder.begin_delta_time().

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def begin_delta_time_start(self, event):
        self.update_handler.begin_delta_time_start(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    @Decorators.intercept_modifier(reset=True)
    def begin_delta_time_end(self, event):
        self.update_handler.begin_delta_time_end(event)

    # #### Key bindings wired by KeyBonder.going_delta_time().

    # The following handlers occur after keybindings are rewired,
    # so there's no need to call the intercept decorator:
    #
    #   NOPE: @Decorators.intercept_modifier

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    def cancel_delta_time(self, event):
        self.update_handler.cancel_delta_time(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    def parts_delta_time(self, event):
        self.update_handler.parts_delta_time(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    def backspace_delta_time(self, event):
        self.update_handler.backspace_delta_time(event)

    # Elsewhere: allow_time_gap (Wired by KeyBonder.command_modifier, too).

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    def final_delta_time_apply(self, event):
        self.update_handler.final_delta_time_apply(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    def final_delta_time_minutes(self, event):
        self.update_handler.final_delta_time_minutes(event)

    @Decorators.debug_log_trace_enter_leave
    @Decorators.refresh_now
    def final_delta_time_hours(self, event):
        self.update_handler.final_delta_time_hours(event)

