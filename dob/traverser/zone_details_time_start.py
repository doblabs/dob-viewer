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
    'ZoneDetails_TimeStart',
]


class ZoneDetails_TimeStart(object):
    """"""

    def add_header_start_time(self):
        self.widgets_start = self.add_header_parts(
            'start', 'start_fmt_local', editable=True,
        )

    def refresh_time_start(self):
        self.refresh_val_widgets(self.widgets_start)

    # ***

    @catch_action_exception
    def edit_time_start(self, event=None, focus=True):
        if focus:
            edit_fact = self.facts_diff.edit_fact
            start_fmt_local = edit_fact.start_fmt_local
            self.widgets_start.orig_val = start_fmt_local
            self.widgets_start.text_area.text = start_fmt_local
            self.edit_time_focus(self.widgets_start)
            return True
        else:
            return self.edit_time_leave(self.widgets_start)

    # ***

    def apply_edit_time_removed_start(edit_fact):
        # Nothing ventured, nothing gained. Ignore deleted start. (We could
        # instead choose to do nothing, or choose to warn-tell user they're
        # an idiot and cannot clear the start time, or we could just behave
        # like a successful edit (by moving focus back to the matter (Fact
        # description) control) but not actually edit anything. Or we could
        # just do nothing. (User can tab-away and then we'll repopulate we
        # unedited time.)
        self.carousel.controller.affirm(edit_fact.start is not None)
        self.widgets_start.text_area.text = edit_fact.start_fmt_local
        if passive:
            # User is tabbing away. We've reset the start, so let them.
            return
        # User hit 'enter'. Annoy them with a warning.
        show_message_cannot_clear_start()

    # ***

    def apply_edit_time_start(self, edit_fact, edit_time):
        if edit_fact.start == edit_time:
            return False
        edit_fact.start = edit_time
        return True

