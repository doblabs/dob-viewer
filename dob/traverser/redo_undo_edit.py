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
"""Fact-editing Redo/Undo Manager"""

from __future__ import absolute_import, unicode_literals

import time
from collections import namedtuple

__all__ = [
    'RedoUndoEdit',
    # Private:
    #   'UndoRedoTuple',
]


UndoRedoTuple = namedtuple(
    'UndoRedoTuple', ('facts', 'time', 'what'),
)


class RedoUndoEdit(object):
    """"""
    def __init__(self, edits_manager):
        self.controller = edits_manager.controller
        self.debug = edits_manager.controller.client_logger.debug
        self.edits_manager = edits_manager
        self.undo = []
        self.redo = []

    # ***

    def append_changes(self, which, urt_changes, whence=''):
        which.append(urt_changes)
        # 2019-01-28: (lb): Added this method, and whence, to make
        # debugging easier for issues related to prev/next links.
        if self.controller.client_config['devmode']:
            self.controller.client_logger.debug(
                '{}: no. changes: {} / to: {}'
                .format(
                    whence,
                    len(urt_changes.pristine),
                    which is self.undo and 'undo' or 'redo',
                ),
            )
            for idx, fact in enumerate(urt_changes.pristine):
                self.controller.client_logger.debug(
                        '\n- # {:d}.: {}\n  prev: {}\n  next: {}'
                    .format(
                        idx,
                        fact.short,
                        fact.prev_fact and fact.prev_fact.short or '<no prev_fact>',
                        fact.next_fact and fact.next_fact.short or '<no next_fact>',
                    ),
                )

    # ***

    def add_undoable(self, copied_facts, what):
        undoable = UndoRedoTuple(copied_facts, time.time(), what)
        # Caller is responsible for calling update_undo_altered later.
        self.append_changes(self.undo, undoable, whence='add_undoable')

    def undo_peek(self):
        try:
            return self.undo[-1]
        except IndexError:
            return UndoRedoTuple([], None, None)

    # ***

    def undoable_changes(self, what, *edit_facts):
        edit_facts = list(filter(None, edit_facts))
        edit_fact_copies = [
            edit_fact.copy() for edit_fact in edit_facts if edit_fact is not None
        ]
        self.controller.affirm(len(edit_fact_copies) > 0)
        undoable_changes = UndoRedoTuple(
            edit_fact_copies, time.time(), what=what,
        )
        return undoable_changes

    # ***

    def remove_undo_if_nothing_changed(self, some_facts):
        latest_changes = self.undo_peek()
        if latest_changes.facts == some_facts:
            # Nothing changed.
            toss_changes = self.undo.pop()
            self.debug('pop!: no.: {}'.format(len(toss_changes)))
            return True
        else:
            # Since we left something different on the undo, the redo is kaput.
            self.redo = []
            return False

    # ***

    def undo_last_edit(self, restore_facts):
        try:
            undo_changes = self.undo.pop()
            self.debug('pop!: no.: {}'.format(len(undo_changes)))
        except IndexError:
            undone = False
        else:
            undone = True
            changes_copies = self.restore_facts(undo_changes, restore_facts)
            self.append_changes(self.redo, changes_copies, whence='undo_last_edit')
        return undone

    def redo_last_undo(self, restore_facts):
        try:
            redo_changes = self.redo.pop()
            self.debug('pop!: no.: {}'.format(len(redo_changes)))
        except IndexError:
            redone = False
        else:
            redone = True
            changes_copies = self.restore_facts(redo_changes, restore_facts)
            self.append_changes(self.undo, changes_copies, whence='redo_last_undo')
        return redone

    def restore_facts(self, fact_changes, restore_facts):
        were_facts = restore_facts(fact_changes.facts)
        latest_changes = UndoRedoTuple(
            were_facts, time=fact_changes.time, what=fact_changes.what,
        )
        return latest_changes

    # ***

    # Combine edits into same undo if similar and made within short time
    # window, e.g, if user keeps adjusting time within 2-½ seconds of
    # previous adjustment, make just one undo object for whole operation.
    DISTINCT_CHANGES_THRESHOLD = 1.333

    def remove_undo_if_same_facts_edited(self, newest_changes):
        latest_changes = self.undo_peek()

        if latest_changes.what != newest_changes.what:
            self.debug('!what: no.: {}'.format(len(newest_changes)))
            return newest_changes

        if (
            (time.time() - latest_changes.time)
            > RedoUndoEdit.DISTINCT_CHANGES_THRESHOLD
        ):
            self.debug('!time: no.: {}'.format(len(newest_changes)))
            return newest_changes

        latest_pks = set([changed.pk for changed in latest_changes.facts])
        if latest_pks != set([edit_fact.pk for edit_fact in newest_changes.facts]):
            self.debug('!pks: no.: {}'.format(len(newest_changes)))
            return newest_changes

        latest_undo = self.undo.pop()
        self.debug('pop!: no.: {}'.format(len(latest_undo)))
        return latest_undo

