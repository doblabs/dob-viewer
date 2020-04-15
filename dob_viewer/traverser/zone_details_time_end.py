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
    'ZoneDetails_TimeEnd',
)


class ZoneDetails_TimeEnd(object):
    """"""

    def __init__(self):
        super(ZoneDetails_TimeEnd, self).__init__()

    def add_header_end_time(self):
        self.widgets_end = self.add_header_section(
            'end', 'end_fmt_local_nowwed', editable=True,
            mouse_handler=self.header_time_end_mouse_handler,
        )

    def header_time_end_mouse_handler(self, mouse_event):
        self.zone_manager.toggle_focus_time_end(event=None)
        self.zone_manager.ppt_control_buffer_avoid_selection(
            self.widgets_end.text_area.control,
            mouse_event,
        )

    def refresh_time_end(self):
        self.refresh_val_widgets(self.widgets_end)

    # ***

    @catch_action_exception
    def edit_time_end(self, event=None, focus=True):
        if focus:
            edit_fact = self.zone_manager.facts_diff.edit_fact
            # Use or-now, unlike start time, because there's on one possible
            # open-ended fact (without an end time) and it'd be the latest fact.
            end_fmt_local_or_now = edit_fact.end_fmt_local_or_now
            self.widgets_end.orig_val = end_fmt_local_or_now
            self.widgets_end.text_area.text = end_fmt_local_or_now
            self.edit_time_focus(self.widgets_end)
            return True
        else:
            return self.edit_time_leave(self.widgets_end)

    # ***

    def apply_edit_time_removed_end(self, edit_fact):
        if not edit_fact.end:
            # Already cleared; nothing changed. Return True to not show
            # dialog message; apply_edit_time_end is called but returns
            # immediately.
            return True
        if self.carousel.edits_manager.conjoined.is_final_fact(edit_fact):
            # First if-branch should've handled, not us!
            self.carousel.controller.affirm(False)
            return True

        edits_manager = self.carousel.edits_manager
        edit_next = edits_manager.editable_fact_next(edit_fact)
        if (
            edit_next.is_gap
            and self.carousel.edits_manager.conjoined.is_final_fact(edit_next)
        ):
            # Use case: User sets end time of active Fact, then tabs away
            # and tabs back, presses Ctrl-U to clear the time entry, then
            # tabs away. Remove Gap Fact and make Fact active again.
            # - Return True so apply_edit_time_end is called.
            return True
        else:
            self.widgets_end.text_area.text = edit_fact.end_fmt_local_or_now
            return False

    # ***

    def apply_edit_time_end(self, edit_fact, edit_time, verify_fact_times):
        if edit_fact.end == edit_time:
            # Nothing changed.
            return False
        edited_facts = [edit_fact]
        edits_manager = self.carousel.edits_manager
        # Make undoable.
        was_fact = edit_fact.copy()
        undoable_facts = [was_fact]
        # After apply_edit_time_removed_end, for editable_fact_next to not die.
        was_time = edit_fact.end
        if edit_time is None:
            edit_fact.end = None
        # Prohibit completely shadowing other facts' time windows, but allow
        # changing one fact's times to shorten the times of prev or next fact.
        edit_next = edits_manager.editable_fact_next(edit_fact)
        best_time = edit_time
        if best_time and edit_next and edit_next.end and (best_time > edit_next.end):
            # Adjust adjacent fact's time width to be no less that fact_min_delta.
            min_delta = int(self.carousel.controller.config['time.fact_min_delta'])
            # We do not want to make momentaneous facts, so use at least 1 minute.
            min_delta = max(1, min_delta)
            best_time = edit_next.end - timedelta(minutes=min_delta)
            if edit_next and edit_next.start and (best_time < edit_next.start):
                best_time = edit_next.start
        edit_fact.end = best_time
        # Verify edit_fact.start < edit_fact.end.
        if not verify_fact_times(edit_fact):
            edit_fact.end = was_time
            return False
        # If the edited time encroached on the neighbor, or if the neighbor
        # is an unedited gap fact, edit thy neighbor.
        if edit_next:
            if ((
                edit_next.start
                and edit_fact.end
                and (edit_fact.end > edit_next.start)
            ) or edit_next.is_gap
            ):
                undoable_facts.append(edit_next.copy())
                edit_next.start = was_time
                edited_facts.append(edit_next)
            if edit_fact.end == edit_next.start:
                edit_fact.next_fact = edit_next
                edit_next.prev_fact = edit_fact
            else:
                edit_fact.next_fact = None
                edit_next.prev_fact = None
        else:
            edit_fact.next_fact = None
        edits_manager.add_undoable(undoable_facts, what='header-edit')
        edits_manager.apply_edits(*edited_facts)
        if edit_time is None:
            # (lb): This feels a little kludgy, or like this belongs elsewhere...
            self.carousel.edits_manager.conjoined.pop_final_gap_fact()
        return True

