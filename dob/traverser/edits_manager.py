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
"""Fact Editing State Machine"""

from __future__ import absolute_import, unicode_literals

from .clipboard_edit import ClipboardEdit
from .facts_manager import FactsManager
from .group_chained import sorted_facts_list
from .redo_undo_edit import RedoUndoEdit
from .start_end_edit import StartEndEdit

__all__ = [
    'EditsManager',
]


class EditsManager(object):
    """"""
    def __init__(
        self,
        controller,
        edit_facts=None,
        orig_facts=None,
        dirty_callback=None,
        error_callback=None,
    ):
        self.controller = controller
        self.setup_editing(edit_facts, orig_facts)
        self._dirty_callback = dirty_callback
        self.error_callback = error_callback

    # ***

    def setup_editing(self, edit_facts, orig_facts):
        """"""
        self.setup_container(edit_facts, orig_facts)
        self.setup_edit_facts(edit_facts)
        self.setup_review_confirmation()
        self.setup_edit_help()

    # ***

    def setup_container(self, edit_facts, orig_facts):
        def _setup_container():
            orig_lkup = orig_facts_lookup(orig_facts)
            apply_orig_facts(edit_facts, orig_lkup)
            self.conjoined = FactsManager(
                self.controller, on_jumped_fact=self.jumped_fact,
            )
            self.add_facts(edit_facts)

        def orig_facts_lookup(orig_facts):
            orig_lkup = orig_facts or {}
            if isinstance(orig_lkup, list):
                orig_lkup = {fact.pk: fact for fact in orig_lkup}
            return orig_lkup

        def apply_orig_facts(edit_facts, orig_lkup):
            for edit_fact in edit_facts:
                try:
                    edit_fact.orig_fact = orig_lkup[edit_fact.pk]
                except KeyError:
                    edit_fact.orig_fact = edit_fact

        _setup_container()

    def add_facts(self, more_facts):
        for fact in more_facts:
            if fact.orig_fact is None:
                # Rather than be self-referential and set, say, fact.orig_fact = fact,
                # we use a magic placeholder, 0, that happens to be non-truthy, and
                # indicates that this fact is the original, unedited copy of itself.
                fact.orig_fact = 0
        self.conjoined.add_facts(more_facts)

    def setup_edit_facts(self, edit_facts):
        # Dirty facts, on stand up, will only include import facts, or fact
        # entered on command line; but will ignore fact read from store, e.g.,
        # `dob edit -1` will start up with an empty self.edit_facts (and the
        # one fact loaded from the store will be help in the conjoined.groups).
        self.edit_facts = {fact.pk: fact for fact in edit_facts if fact.dirty}

    # ***

    def setup_review_confirmation(self):
        self.verify_fact_pks = set([fact.pk for fact in self.conjoined.facts])
        self.viewed_fact_pks = set()

    # ***

    def setup_edit_help(self):
        self.setup_redo_undo()
        self.setup_clipboard()
        self.setup_time_edit()

    def setup_redo_undo(self):
        self.redo_undo = RedoUndoEdit(self)

    def setup_clipboard(self):
        self.clipboard = ClipboardEdit(self)

    def setup_time_edit(self):
        self.time_edit = StartEndEdit(self)

    # ***

    def dirty_callback(self):
        if self._dirty_callback is None:
            return
        self._dirty_callback(self)

    @property
    def is_dirty(self):
        return len(self.edit_facts) > 0

    # ***

    @property
    def curr_fact(self):
        return self.conjoined.curr_fact

    @curr_fact.setter
    def curr_fact(self, curr_fact):
        """"""
        self.controller.client_logger.debug('{}'.format(curr_fact.short))
        if self.conjoined.curr_fact is not curr_fact:
            self.clipboard.reset_paste()
        self.conjoined.curr_fact = curr_fact
        self.viewed_fact_pks.add(curr_fact.pk)

    def jumped_fact(self, jump_fact):
        # Jump to shim to the setter.
        self.curr_fact = jump_fact

    @property
    def user_viewed_all_new_facts(self):
        return self.verify_fact_pks.issubset(self.viewed_fact_pks)

    @property
    def curr_edit(self):
        """
        Returns the currently edited fact, or the original fact if
        nothing being edited. Because this might return the original,
        uneditable fact, he caller is not expected to edit the fact.
        (See editable_fact() for retrieving the editable equivalent
        of this function.)
        """
        try:
            return self.edit_facts[self.curr_fact.pk]
        except KeyError:
            return self.curr_fact

    @property
    def curr_orig(self):
        return self.curr_fact.orig_fact or self.curr_fact

    # ***

    @property
    def curr_fact_group_count(self):
        return len(self.conjoined.curr_group)

    @property
    def curr_fact_group_index(self):
        return self.conjoined.group_index

    # ***

    @property
    def prepared_facts(self):
        prepared_facts_from_edit = sorted_facts_list(self.edit_facts.values())
        prepared_facts_from_view = [
            fact for fact in self.conjoined.facts if fact.pk < 0 or fact.dirty
        ]
        self.controller.affirm(prepared_facts_from_edit == prepared_facts_from_view)
        return prepared_facts_from_edit

    # ***

    def editable_fact(self, ref_fact=None):
        self.controller.client_logger.debug(
            'ref_fact: {}'.format(ref_fact and ref_fact.short),
        )
        # Copy Fact on demand for user to edit, if we haven't made one already.
        # Note that ref_fact is only set from restore_edit_fact, i.e., a fact
        # from the redo_undo stack.
        ref_fact = ref_fact or self.curr_fact
        try:
            edit_fact = self.edit_facts[ref_fact.pk]
            # On dob-import, the original import facts are put in self.edit_facts.
            # So make a copy if what's in edit_facts is the original. (Later, when
            # update_lookups is called via update_edited_fact to update edit_facts,
            # we'll reference this new copy (and this new copy will keep the orig_fact
            # object alive).)
            if not edit_fact.orig_fact:
                self.controller.affirm(edit_fact.orig_fact is 0)
                edit_fact = edit_fact.copy()
            elif edit_fact is self.curr_fact:
                # Don't edit the curr_fact, which is in conjoined.groups,
                # because it could change conjoined.groups[].sorty_tuple,
                # which then creates issues later when groups.index is
                # called in conjoined.update_fact.
                edit_fact = edit_fact.copy()
        except KeyError:
            # Use the latest version of the fact, not orig_fact.
            edit_fact = ref_fact.copy()
            self.controller.affirm(
                (edit_fact.orig_fact is ref_fact)
                or (edit_fact.orig_fact is ref_fact.orig_fact)
            )
            # (lb): Fact might later be placed in self.edit_facts via
            # update_edited_fact if the operation that needs edit_fact
            # actually changes it.
        return edit_fact

    def undoable_editable_fact(self, what, edit_fact=None):
        # Always push the Fact onto the undo stack, should it be edited.
        # The caller will call recompose_lookups() after editing, which
        # might pop the Fact if the user did not edit anything.
        if edit_fact is None:
            edit_fact = self.editable_fact()
        was_fact = edit_fact.copy()
        self.add_undoable([was_fact], what)
        return edit_fact

    def apply_edits(self, *edit_facts):
        # Called on paste, edit-time, and after carousel prompts user for edits.
        edit_facts = list(filter(None, edit_facts))
        self.recompose_lookups(edit_facts)
        self.dirty_callback()

    def add_undoable(self, was_facts, what):
        self.redo_undo.add_undoable(was_facts, what)

    def recompose_lookups(self, edit_facts):
        self.redo_undo.remove_undo_if_nothing_changed(edit_facts)
        for idx, edit_fact in enumerate(edit_facts):
            # 2018-08-04 12:29: EXPLAIN: idx == 0 ?? Why?
            self.manage_edited_dirty_deleted(edit_fact, undelete=(idx == 0))
            self.manage_edited_edit_facts(edit_fact)

    def manage_edited_dirty_deleted(self, edit_fact, undelete=False):
        edit_fact.dirty_reasons.add('unsaved-fact')
        if not undelete:
            return
        # If gap-fact, clear its highlight.
        edit_fact.dirty_reasons.discard('interval-gap')
        edit_fact.deleted = False

    def manage_edited_edit_facts(self, edit_fact):
        orig_fact = edit_fact.orig_fact or edit_fact
        self.update_edited_fact(edit_fact, orig_fact)

    def update_edited_fact(self, edit_fact, orig_fact):
        def _update_edited_fact():
            self.controller.affirm(edit_fact.pk == orig_fact.pk)
            self.controller.affirm(edit_fact is not orig_fact)
            if edit_fact != orig_fact:
                update_lookups(edit_fact)
            else:
                remove_unedited(orig_fact.pk)

        def update_lookups(edit_fact):
            self.edit_facts[edit_fact.pk] = edit_fact
            self.conjoined.update_fact(edit_fact)

        def remove_unedited(fact_pk):
            try:
                # Forget edited fact that's no longer different than orig.
                self.edit_facts.pop(fact_pk)  # Ignoring: popped fact.
            except KeyError:
                pass
            self.conjoined.factory_reset(fact_pk)

        _update_edited_fact()

    # ***

    def stand_up(self):
        self.prepare_curr_fact()

    def prepare_curr_fact(self):
        last_group = self.ensure_view_facts()
        first_last_fact = last_group[0]
        if first_last_fact.unstored:
            # Importing new facts; start with the first.
            self.curr_fact = first_last_fact
        else:
            # Editing existing facts; start with the latest.
            self.curr_fact = last_group[-1]

    def ensure_view_facts(self):
        if not len(list(self.conjoined.facts)):
            self.controller.affirm(len(self.conjoined.groups) == 0)
            latest_fact = self.controller.facts.antecedent(
                ref_time=self.controller.now,
            )
            self.controller.affirm(latest_fact is not None)
            latest_fact.orig_fact = 0
            # FIXME: When latest_fact is None => what's empty carousel state?
            self.add_facts([latest_fact])
        return self.conjoined.groups[-1]

    # ***

    def undo_last_edit(self):
        undone = self.redo_undo.undo_last_edit(self.restore_facts)
        return undone

    def redo_last_undo(self):
        redone = self.redo_undo.redo_last_undo(self.restore_facts)
        return redone

    def restore_facts(self, restore_facts):
        self.curr_fact = restore_facts[0]
        were_facts = self.restore_edit_facts(restore_facts)
        self.dirty_callback()
        return were_facts

    def restore_edit_facts(self, restore_facts):
        were_facts = []
        for restore_fact in restore_facts:
            was_fact = self.restore_edit_fact(restore_fact)
            were_facts.append(was_fact)
        return were_facts

    def restore_edit_fact(self, restore_fact):
        edit_fact = self.editable_fact(restore_fact)
        was_fact = edit_fact.copy()
        edit_fact.restore_edited(restore_fact)
        self.controller.affirm(restore_fact.orig_fact)
        orig_fact = restore_fact.orig_fact or restore_fact
        self.update_edited_fact(edit_fact, orig_fact)
        return was_fact

    # ***

    def fact_copy_activity(self):
        self.clipboard.copy_activity(self.curr_edit)

    def fact_copy_tags(self):
        self.clipboard.copy_tags(self.curr_edit)

    def fact_copy_description(self):
        self.clipboard.copy_description(self.curr_edit)

    def fact_copy_fact(self):
        self.clipboard.copy_fact(self.curr_edit)

    # ***

    def paste_copied_meta(self):
        """"""
        if not self.clipboard.clipboard:
            return None
        edit_fact = self.undoable_editable_fact(what='paste-copied')
        pasted_what = self.clipboard.paste_copied_meta(edit_fact)
        self.apply_edits(edit_fact)
        return pasted_what

    # ***

    def edit_time_adjust(self, delta_time, *attrs):
        edit_fact = self.editable_fact()
        edit_prev, edit_next = self.time_edit.edit_time_adjust(
            edit_fact, delta_time, *attrs,
        )
        self.apply_edits(edit_fact, edit_prev, edit_next)

    # ***

    def editable_fact_prev(self, edit_fact):
        prev_fact = self.jump_fact_dec()
        if prev_fact is None:
            return None
        edit_prev = self.editable_fact()
        _curr_fact = self.jump_fact_inc()
        self.controller.affirm(_curr_fact.pk == edit_fact.pk)
        return edit_prev

    def editable_fact_next(self, edit_fact):
        next_fact = self.jump_fact_inc()
        if next_fact is None:
            return None
        edit_next = self.editable_fact()
        _curr_fact = self.jump_fact_dec()
        self.controller.affirm(_curr_fact.pk == edit_fact.pk)
        return edit_next

    # ***

    def jump_fact_dec(self):
        """"""
        return self.conjoined.jump_fact_dec()

    def jump_fact_inc(self):
        """"""
        return self.conjoined.jump_fact_inc()

    # ***

    def jump_day_dec(self):
        """"""
        return self.conjoined.jump_day_dec()

    def jump_day_inc(self):
        """"""
        return self.conjoined.jump_day_inc()

    # ***

    def jump_rift_dec(self):
        """"""
        self.conjoined.jump_rift_dec()

    def jump_rift_inc(self):
        """"""
        self.conjoined.jump_rift_inc()

