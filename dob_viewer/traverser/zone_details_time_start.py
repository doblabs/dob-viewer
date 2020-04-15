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

"""Zone Details End Time Code (for easier diff-meld against Start Time Code)"""

from datetime import timedelta

from .exceptions import catch_action_exception

__all__ = (
    'ZoneDetails_TimeStart',
)


class ZoneDetails_TimeStart(object):
    """"""

    def __init__(self):
        super(ZoneDetails_TimeStart, self).__init__()

    def add_header_start_time(self):
        self.widgets_start = self.add_header_section(
            'start', 'start_fmt_local', editable=True,
            mouse_handler=self.header_time_start_mouse_handler,
        )

    def header_time_start_mouse_handler(self, mouse_event):
        self.zone_manager.toggle_focus_time_start(event=None)
        self.zone_manager.ppt_control_buffer_avoid_selection(
            self.widgets_start.text_area.control,
            mouse_event,
        )

    def refresh_time_start(self):
        self.refresh_val_widgets(self.widgets_start)

    # ***

    @catch_action_exception
    def edit_time_start(self, event=None, focus=True):
        if focus:
            edit_fact = self.zone_manager.facts_diff.edit_fact
            start_fmt_local = edit_fact.start_fmt_local
            self.widgets_start.orig_val = start_fmt_local
            # Styling/Stylit note: PPT does not let you set format tuples
            # on TextArea text, i.e., text_area.text = [('class:foo', 'bar')]
            # would fail terribly. See elsewhere in the code where we are able
            # to use a SimpleLexer to stylize the input control.
            self.widgets_start.text_area.text = start_fmt_local
            self.edit_time_focus(self.widgets_start)
            return True
        else:
            return self.edit_time_leave(self.widgets_start)

    # ***

    def apply_edit_time_removed_start(self, edit_fact, passive=False):
        # Nothing ventured, nothing gained. Ignore deleted start. (We could
        # instead choose to do nothing, or choose to warn-tell user they're
        # an idiot and cannot clear the start time, or we could just behave
        # like a successful edit (by moving focus back to the matter (Fact
        # description) control) but not actually edit anything. Or we could
        # just do nothing. (User can tab-away and then we'll repopulate we
        # unedited time.)
        self.carousel.controller.affirm(edit_fact.start)
        self.widgets_start.text_area.text = edit_fact.start_fmt_local
        if passive:
            # User is tabbing away. We've reset the start, so let them.
            return True
        # User hit 'enter'. Annoy them with a warning.
        return False

    # ***

    def apply_edit_time_start(self, edit_fact, edit_time, verify_fact_times):
        if edit_fact.start == edit_time:
            # Nothing changed.
            return False
        edited_facts = [edit_fact]
        edits_manager = self.carousel.edits_manager
        # Make undoable.
        was_fact = edit_fact.copy()
        undoable_facts = [was_fact]
        # Prohibit completely shadowing other facts' time windows, but allow
        # changing one fact's times to shorten the times of prev or next fact.
        edit_prev = edits_manager.editable_fact_prev(edit_fact)
        best_time = edit_time
        if edit_prev and edit_prev.start and (best_time < edit_prev.start):
            # Adjust adjacent fact's time width to be no less that fact_min_delta.
            min_delta = int(self.carousel.controller.config['time.fact_min_delta'])
            # We do not want to make momentaneous facts, so use at least 1 minute.
            min_delta = max(1, min_delta)
            best_time = edit_prev.start + timedelta(minutes=min_delta)
            if edit_prev and edit_prev.end and (best_time > edit_prev.end):
                best_time = edit_prev.end
        was_time = edit_fact.start
        edit_fact.start = best_time
        # Verify edit_fact.start < edit_fact.end.
        if not verify_fact_times(edit_fact):
            edit_fact.start = was_time
            return False
        # If the edited time encroached on the neighbor, or if the neighbor
        # is an unedited gap fact, edit thy neighbor.
        if edit_prev:
            if (
                (edit_fact.start < edit_prev.end)
                or edit_prev.is_gap
            ):
                undoable_facts.append(edit_prev.copy())
                edit_prev.end = edit_fact.start
                edited_facts.append(edit_prev)
            if edit_fact.start == edit_prev.end:
                edit_fact.prev_fact = edit_prev
                edit_prev.next_fact = edit_fact
            else:
                edit_fact.prev_fact = None
                edit_prev.next_fact = None
        else:
            edit_fact.prev_fact = None
        edits_manager.add_undoable(undoable_facts, what='header-edit')
        edits_manager.apply_edits(*edited_facts)
        return True

