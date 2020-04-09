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

"""Fact-editing Redo/Undo Manager"""

import time
from collections import namedtuple

__all__ = (
    'RedoUndoEdit',
    'UndoRedoTuple',
)


UndoRedoTuple = namedtuple(
    'UndoRedoTuple', ('pristine', 'altered', 'time', 'what'),
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
        if self.controller.config['dev.catch_errors']:  # More devmode than catch_errors.
            facts_shorts = ''
            if urt_changes.altered:
                for idx, fact in enumerate(urt_changes.altered):
                    facts_shorts += ('\n- # {:d}.: {}'.format(idx, fact.short,))
            self.controller.client_logger.debug(
                '{}: no. changes: {} / to: {}{}'
                .format(
                    whence,
                    len(urt_changes.pristine),
                    which is self.undo and 'undo' or 'redo',
                    facts_shorts,
                ),
            )

    def clear_changes(self, which, whence=''):
        which.clear()
        if self.controller.config['dev.catch_errors']:
            self.controller.client_logger.debug(
                '{}: cleared changes from: {}'
                .format(
                    whence,
                    which is self.undo and 'undo' or 'redo',
                ),
            )

    # ***

    def add_undoable(self, copied_facts, what):
        undoable = UndoRedoTuple(copied_facts, None, time.time(), what)
        # Caller is responsible for calling update_undo_altered later.
        self.append_changes(self.undo, undoable, whence='add_undoable')

    def undo_peek(self):
        try:
            return self.undo[-1]
        except IndexError:
            return UndoRedoTuple([], [], None, None)

    # ***

    def undoable_changes(self, what, *edit_facts):
        edit_facts = list(filter(None, edit_facts))
        edit_fact_copies = [
            edit_fact.copy() for edit_fact in edit_facts if edit_fact is not None
        ]
        self.controller.affirm(len(edit_fact_copies) > 0)
        undoable_changes = UndoRedoTuple(
            edit_fact_copies, edit_facts, time.time(), what=what,
        )
        return undoable_changes

    # ***

    def remove_undo_if_nothing_changed(self, edit_facts):
        last_edits = self.undo_peek()
        if last_edits.pristine == edit_facts:
            # Nothing changed.
            toss_changes = self.undo.pop()
            self.debug('pop!: no.: {}'.format(len(toss_changes)))
            return None
        else:
            # Since what's on the undo is different, the redo is kaput.
            self.clear_changes(self.redo, 'remove_undo_if_nothing_changed')
            return last_edits.pristine

    # ***

    def update_undo_altered(self, edit_facts, append=False):
        try:
            undo_changes = self.undo.pop()
        except IndexError:
            self.controller.affirm(append)
            return

        self.controller.affirm(
            (
                (not append)
                and (
                    (undo_changes.altered is None)
                    or (undo_changes.altered == edit_facts)
                )
            )
            or (
                append
                and (
                    not set([fact.pk for fact in undo_changes.altered])
                    .intersection(set([fact.pk for fact in edit_facts]))
                )
            )
        )

        if append:
            edit_facts = undo_changes.altered + edit_facts

        undoable = UndoRedoTuple(
            undo_changes.pristine, edit_facts, undo_changes.time, undo_changes.what,
        )

        self.append_changes(
            self.undo,
            undoable,
            whence='update_undo_altered-{}'.format(undoable.what),
        )

        # This seals the deal; what's on the undo is different, and the redo is kaput.
        self.clear_changes(self.redo, 'update_undo_altered')

    # ***

    def undo_last_edit(self, restore_facts):
        try:
            undo_changes = self.undo.pop()
            self.debug('pop!: no.: {}'.format(len(undo_changes)))
        except IndexError:
            undone = False
        else:
            undone = True
            if restore_facts is not None:
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
        restore_facts(fact_changes.pristine, fact_changes.altered)
        latest_changes = UndoRedoTuple(
            pristine=fact_changes.altered,
            altered=fact_changes.pristine,
            time=fact_changes.time,  # Not really meaningful anymore.
            what=fact_changes.what,
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
            self.debug('!what: no.: {}'.format(len(newest_changes.pristine)))
            return newest_changes

        if (
            (time.time() - latest_changes.time)
            > RedoUndoEdit.DISTINCT_CHANGES_THRESHOLD
        ):
            self.debug('!time: no.: {}'.format(len(newest_changes.pristine)))
            return newest_changes

        latest_pks = set([changed.pk for changed in latest_changes.pristine])
        if latest_pks != set([edit_fact.pk for edit_fact in newest_changes.pristine]):
            self.debug('!pks: no.: {}'.format(len(newest_changes.pristine)))
            return newest_changes

        latest_undo = self.undo.pop()
        self.debug('pop!: no.: {}'.format(len(latest_undo.pristine)))
        return latest_undo

