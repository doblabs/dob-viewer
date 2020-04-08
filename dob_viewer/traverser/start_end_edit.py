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

"""Fact Editing Start and End Time Adjuster"""

from .redo_undo_edit import UndoRedoTuple

__all__ = (
    'StartEndEdit',
)


class StartEndEdit(object):
    """"""
    def __init__(self, edits_manager):
        self.controller = edits_manager.controller
        # MAYBE/2019-01-31: (lb): This class is tightly coupled.
        #  We might as well concede defeat and make this class a
        #  part of an EditsManager hierarchy (like the FactsManager
        #  classes).
        self.restore_facts = edits_manager.restore_facts
        self.editable_fact = edits_manager.editable_fact
        self.editable_fact_next = edits_manager.editable_fact_next
        self.editable_fact_prev = edits_manager.editable_fact_prev
        self.redo_undo = edits_manager.redo_undo

    # ***

    def edit_time_adjust(self, delta_time, *attrs):
        def _edit_time_adjust():
            edit_fact = self.editable_fact()
            edit_prev = self.time_adjust_editable_prev(edit_fact, *attrs)
            edit_next = self.time_adjust_editable_next(edit_fact, *attrs)

            debug_log_facts('edit-time-begin', edit_fact, edit_prev, edit_next)

            edit_what = 'adjust-time-{}'.format(
                delta_time.total_seconds() >= 0 and 'pos' or 'neg',
            )
            # Get an UndoRedoTuple from a copy of the Facts we're about to edit.
            # And set UndoRedoTuple.altered to the new copies.
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

            # (lb): Ug, more coupling. Because we are managing the redo-undo stack
            # specially here (possibly removing the latest undo, and squishing it
            # with the new edits), we do not want to call edits_manager.apply_edits,
            # which calls update_redo_undo_and_conjoined, which fiddles with redo_undo.
            # Instead, do things piecemeal: pop the latest undo; squish it; push it back;
            # clear the redo; and use the restore_facts method to fix wiring (update the
            # edits_manager.edit_facts and facts_manager.by_pk lookups, and update the
            # facts_manager fact-groups).

            # If same Facts edited with same tool within DISTINCT_CHANGES_THRESHOLD
            # time, pop the previous undo.
            last_undo_or_newest_changes = (
                self.redo_undo.remove_undo_if_same_facts_edited(
                    newest_changes,
                )
            )
            self.controller.affirm(
                (newest_changes is last_undo_or_newest_changes)
                or (newest_changes.pristine == last_undo_or_newest_changes.altered)
            )

            # Create the freshest undo. It might be squished with an earlier
            # undo created by the user within DISTINCT_CHANGES_THRESHOLD ago,
            # in which case, the pristine Facts are from the previous undo.
            # In all cases, the altered Facts are the ones we just edited.
            undoable = UndoRedoTuple(
                last_undo_or_newest_changes.pristine,
                newest_changes.altered,
                last_undo_or_newest_changes.time,
                last_undo_or_newest_changes.what,
            )

            # In lieu of having called add_undoable, add the changes to the undo stack.
            self.redo_undo.append_changes(
                self.redo_undo.undo,
                undoable,
                whence='edit_time_adjust',
            )
            # This invalidates the redo stack.
            self.redo_undo.clear_changes(self.redo_undo.redo, 'edit_time_adjust')

            self.restore_facts(
                newest_changes.altered,
                # This is a little tricky: the Facts currently wired in the
                # FactsManager were altered by the previous Undo that we might
                # be replacing if within DISTINCT_CHANGES_THRESHOLD, so use
                # these Facts to fix the wiring.
                newest_changes.pristine,
            )

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
            # The ongoing, un-ended, active Fact.
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

