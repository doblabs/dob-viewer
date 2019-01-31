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
"""Fact Editing Start and End Time Adjuster"""

from __future__ import absolute_import, unicode_literals

__all__ = [
    'StartEndEdit',
]


class StartEndEdit(object):
    """"""
    def __init__(self, edits_manager):
        self.controller = edits_manager.controller
        self.redo_undo = edits_manager.redo_undo
        self.editable_fact_prev = edits_manager.editable_fact_prev
        self.editable_fact_next = edits_manager.editable_fact_next

    # ***

    def edit_time_adjust(self, edit_fact, delta_time, *attrs):
        def _edit_time_adjust():
            edit_prev = self.time_adjust_editable_prev(edit_fact, *attrs)
            edit_next = self.time_adjust_editable_next(edit_fact, *attrs)

            debug_log_facts('edit-time-begin', edit_fact, edit_prev, edit_next)

            edit_what = 'adjust-time-{}'.format(
                delta_time.total_seconds() >= 0 and 'pos' or 'neg',
            )
            newest_changes = self.redo_undo.undoable_changes(
                edit_what, edit_fact, edit_prev, edit_next,
            )

            self.edit_time_adjust_time(edit_fact, edit_prev, delta_time, 'start', *attrs)
            self.edit_time_adjust_time(edit_fact, edit_next, delta_time, 'end', *attrs)

            if edit_prev and edit_prev.end > edit_fact.start:
                edit_prev.end = edit_fact.start
            if edit_next and edit_next.start < edit_fact.end:
                edit_next.start = edit_fact.end

            debug_log_facts('edit-time-final', edit_fact, edit_prev, edit_next)

            last_undo_or_newest_changes = (
                self.redo_undo.remove_undo_if_same_facts_edited(
                    newest_changes,
                )
            )

            # In lieu of having called add_undoable, add the changes to the undo stack.
            self.redo_undo.undo.append(last_undo_or_newest_changes)

            return edit_prev, edit_next

        def debug_log_facts(prefix, edit_fact, edit_prev, edit_next):
            self.controller.client_logger.debug(
                '{}\n- edit: {}\n- prev: {}\n- next: {}'.format(
                    prefix,
                    edit_fact and edit_fact.short or '<no such fact>',
                    edit_prev and edit_prev.short or '<no such fact>',
                    edit_next and edit_next.short or '<no such fact>',
                ),
            )

        return _edit_time_adjust()

    # ***

    def time_adjust_editable_prev(self, edit_fact, *attrs):
        if 'start' not in attrs:
            return None
        return self.editable_fact_prev(edit_fact)

    def time_adjust_editable_next(self, edit_fact, *attrs):
        if 'end' not in attrs:
            return None
        return self.editable_fact_next(edit_fact)

    # ***

    def edit_time_adjust_time(
        self, edit_fact, neighbor, delta_time, start_or_end, *attrs
    ):
        if start_or_end not in attrs:
            return

        curr_time = getattr(edit_fact, start_or_end)
        if curr_time is None:
            # The ongoing, un-ended Fact.
            self.controller.affirm(start_or_end == 'end')
            # NOTE: Not using controller.now.
            curr_time = self.controller.store.now_tz_aware()
        new_time = curr_time + delta_time

        if start_or_end == 'start':
            if edit_fact.end and new_time > edit_fact.end:
                new_time = edit_fact.end
        else:
            self.controller.affirm(start_or_end == 'end')
            if new_time < edit_fact.start:
                new_time = edit_fact.start

        incrementing = delta_time.total_seconds() > 0
        new_time = self.edit_time_check_edge(
            new_time, neighbor, start_or_end, incrementing,
        )
        setattr(edit_fact, start_or_end, new_time)

    def edit_time_check_edge(self, new_time, neighbor, start_or_end, incrementing):
        if neighbor is None:
            return new_time
        if start_or_end == 'start':
            if new_time < neighbor.start:
                self.controller.affirm(not incrementing)
                new_time = neighbor.start
            neighbor.end = new_time
        else:
            self.controller.affirm(start_or_end == 'end')
            if neighbor.end and new_time > neighbor.end:
                self.controller.affirm(incrementing)
                new_time = neighbor.end
                self.controller.affirm(neighbor.start == neighbor.end)
            else:
                neighbor.start = new_time
        return new_time

