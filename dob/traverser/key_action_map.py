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
"""Key Binding Action Handler Shim"""

from __future__ import absolute_import, unicode_literals

from .zone_content import ZoneContent

__all__ = [
    'KeyActionMap',
]


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

    @ZoneContent.Decorators.reset_showing_help
    def ignore_key_press_noop(self, event):
        """"""
        pass

    # ###

    def cancel_command(self, event):
        self.carousel.cancel_command(event)

    def cancel_softly(self, event):
        self.carousel.cancel_softly(event)

    def finish_command(self, event):
        self.carousel.finish_command(event)

    # ###

    def focus_next(self, event):
        self.zone_manager.focus_next(event)

    def focus_previous(self, event):
        self.zone_manager.focus_previous(event)

    # ***

    def scroll_left(self, event):
        self.zone_manager.scroll_left(event)

    def scroll_right(self, event):
        self.zone_manager.scroll_right(event)

    def scroll_left_day(self, event):
        self.zone_manager.scroll_left_day(event)

    def scroll_right_day(self, event):
        self.zone_manager.scroll_right_day(event)

    def scroll_fact_last(self, event):
        self.zone_manager.scroll_fact_last(event)

    def scroll_fact_first(self, event):
        self.zone_manager.scroll_fact_first(event)

    # ###

    def rotate_help(self, event):
        self.zone_content.rotate_help(event)

    # ***

    def cursor_up_one(self, event):
        self.zone_content.cursor_up_one(event)

    def cursor_down_one(self, event):
        self.zone_content.cursor_down_one(event)

    # ***

    def scroll_up(self, event):
        self.zone_content.scroll_up(event)

    def scroll_down(self, event):
        self.zone_content.scroll_down(event)

    def scroll_top(self, event):
        self.zone_content.scroll_top(event)

    def scroll_bottom(self, event):
        self.zone_content.scroll_bottom(event)

    # ###

    def edit_time_start(self, event):
        self.zone_details.edit_time_start(event)

    def edit_time_end(self, event):
        self.zone_details.edit_time_end(event)

    # ###

    def edit_time_decrement_start(self, event):
        self.update_handler.edit_time_decrement_start(event)

    def edit_time_increment_start(self, event):
        self.update_handler.edit_time_increment_start(event)

    def edit_time_decrement_end(self, event):
        self.update_handler.edit_time_decrement_end(event)

    def edit_time_increment_end(self, event):
        self.update_handler.edit_time_increment_end(event)

    def edit_time_decrement_both(self, event):
        self.update_handler.edit_time_decrement_both(event)

    def edit_time_increment_both(self, event):
        self.update_handler.edit_time_increment_both(event)

    def fact_split(self, event):
        self.update_handler.fact_split(event)

    def fact_wipe(self, event):
        self.update_handler.fact_wipe(event)

    def fact_copy_fact(self, event):
        self.update_handler.fact_copy_fact(event)

    def fact_cut(self, event):
        self.update_handler.fact_cut(event)

    def fact_paste(self, event):
        self.update_handler.fact_paste(event)

    def fact_copy_activity(self, event):
        self.update_handler.fact_copy_activity(event)

    def fact_copy_tags(self, event):
        self.update_handler.fact_copy_tags(event)

    def fact_copy_description(self, event):
        self.update_handler.fact_copy_description(event)

