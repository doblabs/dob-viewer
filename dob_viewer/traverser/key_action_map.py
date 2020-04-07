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

from .zone_content import ZoneContent

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

    # #### Key bindings wired by key_bonds_normal().

    # ***

    @Decorators.debug_log_trace_enter_leave
    def rotate_help(self, event):
        self.zone_content.rotate_help(event)

    # ***

    @Decorators.debug_log_trace_enter_leave
    def dev_breakpoint(self, event):
        self.carousel.dev_breakpoint(event)

    # ***

    # Next/Prev: Fact

    @Decorators.debug_log_trace_enter_leave
    def jump_fact_dec(self, event):
        self.zone_manager.jump_fact_dec(event)

    @Decorators.debug_log_trace_enter_leave
    def jump_fact_inc(self, event):
        try:
            self.zone_manager.jump_fact_inc(event)
        except Exception:
            # 2019-12-03 01:18: Raised on add-tag then save. Don't remember jumping.
            self.carousel.controller.affirm(False)
            pass

    # Next/Prev: Day

    @Decorators.debug_log_trace_enter_leave
    def jump_day_dec(self, event):
        self.zone_manager.jump_day_dec(event)

    @Decorators.debug_log_trace_enter_leave
    def jump_day_inc(self, event):
        self.zone_manager.jump_day_inc(event)

    # Next/Prev: Rift

    @Decorators.debug_log_trace_enter_leave
    def jump_rift_dec(self, event):
        self.zone_manager.jump_rift_dec(event)

    @Decorators.debug_log_trace_enter_leave
    def jump_rift_inc(self, event):
        self.zone_manager.jump_rift_inc(event)

    # ***

    @Decorators.debug_log_trace_enter_leave
    def cursor_up_one(self, event):
        self.zone_content.cursor_up_one(event)

    @Decorators.debug_log_trace_enter_leave
    def cursor_down_one(self, event):
        self.zone_content.cursor_down_one(event)

    # #### Key bindings wired by key_bonds_save_and_quit().

    @Decorators.debug_log_trace_enter_leave
    def save_edited_and_live(self, event):
        self.carousel.save_edited_and_live(event)

    @Decorators.debug_log_trace_enter_leave
    def save_edited_and_exit(self, event):
        self.carousel.save_edited_and_exit(event)

    @Decorators.debug_log_trace_enter_leave
    def cancel_command(self, event):
        self.carousel.cancel_command(event)

    @Decorators.debug_log_trace_enter_leave
    def cancel_softly(self, event):
        was_helping = self.zone_content.on_reset_hide_help()
        if was_helping:
            return
        self.carousel.cancel_softly(event)

    # ***

    @Decorators.debug_log_trace_enter_leave
    @ZoneContent.Decorators.reset_showing_help
    def ignore_key_press_noop(self, event):
        pass

    # #### Key bindings wired by key_bonds_normal().

    @Decorators.debug_log_trace_enter_leave
    def scroll_up(self, event):
        self.zone_content.scroll_up(event)

    @Decorators.debug_log_trace_enter_leave
    def scroll_down(self, event):
        self.zone_content.scroll_down(event)

    @Decorators.debug_log_trace_enter_leave
    def scroll_top(self, event):
        self.zone_content.scroll_top(event)

    @Decorators.debug_log_trace_enter_leave
    def scroll_bottom(self, event):
        self.zone_content.scroll_bottom(event)

    # ***

    @Decorators.debug_log_trace_enter_leave
    def edit_time_start(self, event):
        self.zone_manager.toggle_focus_time_start(event)

    @Decorators.debug_log_trace_enter_leave
    def edit_time_end(self, event):
        self.zone_manager.toggle_focus_time_end(event)

    # #### Key bindings wired by key_bonds_widget_focus().

    @Decorators.debug_log_trace_enter_leave
    def focus_next(self, event):
        self.zone_manager.focus_next(event)

    @Decorators.debug_log_trace_enter_leave
    def focus_previous(self, event):
        self.zone_manager.focus_previous(event)

    # #### Key bindings wired by key_bonds_update().

    @Decorators.debug_log_trace_enter_leave
    def edit_fact(self, event):
        self.update_handler.edit_fact(event)

    @Decorators.debug_log_trace_enter_leave
    def edit_actegory(self, event):
        self.update_handler.edit_actegory(event)

    @Decorators.debug_log_trace_enter_leave
    def edit_description(self, event):
        self.update_handler.edit_description(event)

    @Decorators.debug_log_trace_enter_leave
    def edit_tags(self, event):
        self.update_handler.edit_tags(event)

    @Decorators.debug_log_trace_enter_leave
    def edit_time_decrement_start(self, event):
        self.update_handler.edit_time_decrement_start(event)

    @Decorators.debug_log_trace_enter_leave
    def edit_time_increment_start(self, event):
        self.update_handler.edit_time_increment_start(event)

    @Decorators.debug_log_trace_enter_leave
    def edit_time_decrement_end(self, event):
        self.update_handler.edit_time_decrement_end(event)

    @Decorators.debug_log_trace_enter_leave
    def edit_time_increment_end(self, event):
        self.update_handler.edit_time_increment_end(event)

    @Decorators.debug_log_trace_enter_leave
    def edit_time_decrement_both(self, event):
        self.update_handler.edit_time_decrement_both(event)

    @Decorators.debug_log_trace_enter_leave
    def edit_time_increment_both(self, event):
        self.update_handler.edit_time_increment_both(event)

    @Decorators.debug_log_trace_enter_leave
    def fact_split(self, event):
        self.update_handler.fact_split(event)

    @Decorators.debug_log_trace_enter_leave
    def fact_erase(self, event):
        self.update_handler.fact_erase(event)

    @Decorators.debug_log_trace_enter_leave
    def fact_merge_prev(self, event):
        self.update_handler.fact_merge_prev(event)

    @Decorators.debug_log_trace_enter_leave
    def fact_merge_next(self, event):
        self.update_handler.fact_merge_next(event)

    # #### Key bindings wired by key_bonds_clipboard().

    @Decorators.debug_log_trace_enter_leave
    def fact_copy_fact(self, event):
        self.update_handler.fact_copy_fact(event)

    @Decorators.debug_log_trace_enter_leave
    def fact_cut(self, event):
        self.update_handler.fact_cut(event)

    @Decorators.debug_log_trace_enter_leave
    def fact_paste(self, event):
        self.update_handler.fact_paste(event)

    @Decorators.debug_log_trace_enter_leave
    def fact_copy_activity(self, event):
        self.update_handler.fact_copy_activity(event)

    @Decorators.debug_log_trace_enter_leave
    def fact_copy_tags(self, event):
        self.update_handler.fact_copy_tags(event)

    @Decorators.debug_log_trace_enter_leave
    def fact_copy_description(self, event):
        self.update_handler.fact_copy_description(event)

    # #### Key bindings wired by key_bonds_undo_redo().

    @Decorators.debug_log_trace_enter_leave
    def undo_command(self, event):
        self.update_handler.undo_command(event)

    @Decorators.debug_log_trace_enter_leave
    def redo_command(self, event):
        self.update_handler.redo_command(event)

