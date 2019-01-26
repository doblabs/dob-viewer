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
"""Zone Details End Time Code (for easier diff-meld against Start Time Code)"""

from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from ..helpers.exceptions import catch_action_exception


__all__ = [
    'ZoneDetails_TimeEnd',
]


class ZoneDetails_TimeEnd(object):
    """"""

    def add_header_end_time():
        self.widgets_end = add_header_parts(
            'end', 'end_fmt_local_nowwed', editable=True,
        )

    def refresh_time_end(self):
        self.refresh_val_widgets(self.widgets_end)

    # ***

    @catch_action_exception
    def edit_time_end(self, event=None, focus=True):
        if focus:
            edit_fact = self.facts_diff.edit_fact
            end_fmt_local_or_now = edit_fact.end_fmt_local_or_now
            self.widgets_end.orig_val = end_fmt_local_or_now
            self.widgets_end.text_area.text = end_fmt_local_or_now
            self.edit_time_focus(self.widgets_end)
            return True
        else:
            return self.edit_time_leave(self.widgets_end)

    # ***

    def apply_edit_time_removed_end(edit_fact):
        if edit_fact.end is None:
            # Already cleared; nothing changed.
            return
        if not self.carousel.controller.is_final_fact(edit_fact):
            self.widgets_end.text_area.text = edit_fact.end_fmt_local_or_now
            # Always warn user, whether they hit 'enter' or are tabbing away.
            show_message_cannot_clear_end()
        else:
            edit_fact.end = None
            self.carousel.controller.affirm(False)

    # ***

    def apply_edit_time_end(edit_fact, edit_time):
        if edit_fact.end == edit_time:
            return False
        edit_fact.end = edit_time
        return True

