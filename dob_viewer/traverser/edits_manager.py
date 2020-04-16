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

"""Fact Editing State Machine"""

from ..crud.fact_from_factoid import must_create_fact_from_factoid

from .clipboard_edit import ClipboardEdit
from .facts_manager import FactsManager
from .group_chained import sorted_facts_list
from .redo_undo_edit import RedoUndoEdit
from .start_end_edit import StartEndEdit

__all__ = (
    'EditsManager',
)


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
                self.controller,
                on_jumped_fact=self.jumped_fact,
                on_insert_fact=self.insert_fact,
            )
            self.add_facts(edit_facts)

        def orig_facts_lookup(orig_facts):
            orig_lkup = orig_facts or {}
            if isinstance(orig_lkup, list):
                orig_lkup = {fact.pk: fact for fact in orig_lkup}
            return orig_lkup

        def apply_orig_facts(edit_facts, orig_lkup):
            for edit_fact in edit_facts:
                apply_orig_fact(edit_fact, orig_lkup)

        def apply_orig_fact(edit_fact, orig_lkup):
            self.controller.affirm(edit_fact.orig_fact is None)
            try:
                # NOTE: For facts from the store loaded on start, this is the
                # only reference to them. (For facts loaded later from the
                # store, they're stored on self.edit_facts only until they're
                # edited, then they, too, become just an orig_fact reference
                # on an edit_fact, or a fact on the undo/redo stack.
                edit_fact.orig_fact = orig_lkup[edit_fact.pk]
            except KeyError:
                edit_fact.orig_fact = 0
            if edit_fact.orig_fact:
                # FIXME/2019-01-20: TEST NEW PATH
                self.controller.affirm(False)  # (lb): Not been here yet.
                # FIXME/2019-01-22: If you make empty group, should make time-gap,
                # so group has at least 1 Fact! Should also manage gap-time entry as
                # time-space changes (for any group? or will the inc/dec code figure
                # that out otherwise?? too many edge cases!).
                assign_orig_fact(edit_fact, orig_lkup)
                # Note that claim_time_span changes the group key, but
                # the group has not been added to the conjoined.groups
                # container yet (so no need to use self.fact_group_rekeyed).
                self.conjoined.claim_time_span(*edit_fact.orig_fact.times)

        def assign_orig_fact(edit_fact, orig_lkup):
            self.controller.affirm(edit_fact.orig_fact is not edit_fact)
            self.controller.affirm(edit_fact.orig_fact.orig_fact is None)
            edit_fact.orig_fact.orig_fact = 0

        _setup_container()

    def add_facts(self, more_facts):
        for fact in more_facts:
            if fact.orig_fact is None:
                # Rather than be self-referential and set, say, fact.orig_fact = fact,
                # we use a magic placeholder, 0, that happens to be non-truthy, and
                # indicates that this fact is the original, unedited copy of itself.
                fact.orig_fact = 0  # As opposed to None, means original, unedited copy.
        self.conjoined.add_facts(more_facts)

    def setup_edit_facts(self, edit_facts):
        # Dirty facts, on stand up, will only include import facts, or fact
        # entered on command line; but will ignore fact read from store, e.g.,
        # `dob edit -1` will start up with an empty self.edit_facts (and the
        # one fact loaded from the store will be held in the conjoined.groups).
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
        self.controller.client_logger.debug(
            '\n- curr: {}'.format(curr_fact.short),
        )
        if self.conjoined.curr_fact is not curr_fact:
            self.clipboard.reset_paste()
        self.conjoined.curr_fact = curr_fact
        self.viewed_fact_pks.add(curr_fact.pk)

    def insert_fact(self, gap_fact):
        self.redo_undo.update_undo_altered([gap_fact], append=True)

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
    def edit_fact_count(self):
        return len(self.edit_facts)

    @property
    def edit_fact_index(self):
        return sorted_facts_list(self.edit_facts.values()).index(self.curr_fact)

    # ***

    @property
    def prepared_facts(self):
        """
        Returns list of edited and new facts to persist (to database, export file, etc.).
        """
        prepared_facts_from_edit = sorted_facts_list(self.edit_facts.values())
        prepared_facts_from_view = [
            fact for fact in self.conjoined.facts if fact.dirty
        ]
        self.controller.affirm(prepared_facts_from_edit == prepared_facts_from_view)
        return prepared_facts_from_edit

    # ***

    def editable_fact(self):
        # Copy Fact on demand for user to edit, if we haven't made one already.
        try:
            edit_fact = self.edit_facts[self.curr_fact.pk]
            # On dob-import, the original import facts are put in self.edit_facts.
            # So make a copy if what's in edit_facts is the original. (Later, when
            # update_lookups is called via update_edited_fact to update edit_facts,
            # we'll reference this new copy (and this new copy will keep the orig_fact
            # object alive).)
            if not edit_fact.orig_fact:
                self.controller.affirm(edit_fact.orig_fact == 0)
                edit_fact = edit_fact.copy()
            elif edit_fact is self.curr_fact:
                # (lb): The FactsManager fact-groups are wired with the latest
                # edit of the Fact, so if the user wants to edit a Fact again, be
                # sure to pass them a Fact copy, lest they edit the one that is
                # already part of a fact-group. (Editing a Fact once it is part of
                # a SortedKeyList causes a number of problems. For one, the group
                # key, conjoined.groups[n].sorty_times, returns a different value,
                # but, internally, the _maxes value is unchanged. This causes the
                # group to behave oddly. And the only way to ensure that _maxes is
                # updated is to remove and reinsert the Fact, but to remove the
                # Fact, we need to be able to identify it. Hence, we cannot have
                # other code inadvertently mucking with a Fact once it's been
                # added to the group-fact container. So return a copy.)
                edit_fact = edit_fact.copy()
        except KeyError:
            # Use the latest version of the fact, not orig_fact.
            edit_fact = self.curr_fact.copy()
            self.controller.affirm(
                (edit_fact.orig_fact is self.curr_fact)
                or (edit_fact.orig_fact is self.curr_fact.orig_fact)
            )
            # (lb): Fact might later be placed in self.edit_facts via
            # update_edited_fact if the operation that needs edit_fact
            # actually changes it.
        return edit_fact

    def undoable_editable_fact(self, what, edit_fact=None):
        # Always push the Fact onto the undo stack, should it be edited.
        # The caller calls update_redo_undo_and_conjoined() after editing,
        # which might pop the Fact if the user did not edit anything.
        if edit_fact is None:
            edit_fact = self.editable_fact()
        was_fact = edit_fact.copy()
        self.add_undoable([was_fact], what)
        # Caller is responsible for calling this class' apply_edits later.
        return edit_fact

    def apply_edits(self, *edit_facts):
        # Called on edit-time, and after carousel prompts user for edits.
        # edit_facts is a list of 1 or 2 Facts: the edited Fact, and then
        # maybe a prev or next Fact, if one exists and was affected by a
        # change to the edited Fact's start or end time.
        edit_facts = list(filter(None, edit_facts))
        applied_edits = self.update_redo_undo_and_conjoined(edit_facts)
        if not applied_edits:
            self.controller.affirm(edit_facts[0] == self.curr_fact)
            return
        self.dirty_callback()
        # Show the first edited Fact (and ensure Carousel showing a wired
        # Fact, in case what was curr_fact was removed during the edit).
        self.curr_fact = self.conjoined.locate_wired(edit_facts[0])

    def add_undoable(self, was_facts, what):
        self.redo_undo.add_undoable(was_facts, what)

    def update_redo_undo_and_conjoined(self, edit_facts):
        # edit_facts is 1 or 2 items: current fact, maybe followed by neighbor.
        last_edits = self.redo_undo.remove_undo_if_nothing_changed(edit_facts)
        if last_edits is None:
            return False

        self.manage_edited_dirty_flags(edit_facts)

        self.conjoined.apply_edits(edit_facts, last_edits)

        # Update undo with edited Facts.
        self.redo_undo.update_undo_altered(edit_facts)

        return True

    def manage_edited_dirty_flags(self, edit_facts):
        for idx, edit_fact in enumerate(edit_facts):
            # Only unmark interval-gap if this is the first fact in edit_facts,
            # which indicates user deliberately edited gap-fact; as opposed
            # to if gap-fact is later in edit_facts, and then it was edited
            # by time adjust of another fact. Feels like could be better way.
            is_oldest_fact = idx == 0
            self.manage_edited_dirty_deleted(edit_fact, undelete=is_oldest_fact)
            self.manage_edited_edit_facts(edit_fact)

    def manage_edited_dirty_deleted(self, edit_fact, undelete=False):
        edit_fact.dirty_reasons.add('unsaved-fact')
        if not undelete:
            return

        # If user edited gap-fact, ensure returned by prepared_facts; and clear
        # its gap-fact highlight (i.e., remove 'interval-gap' from dirty_reasons).
        edit_fact.is_gap = False

        # An interval-gap is not necessarily marked deleted,
        #  but if edited, we should make sure it no longer is.
        # Also, if any Fact was marked deleted, but user edited
        #  it, should also make sure not deleted.
        edit_fact.deleted = False

    def manage_edited_edit_facts(self, edit_fact):
        orig_fact = edit_fact.orig_fact or edit_fact
        self.update_edited_fact(edit_fact, orig_fact)

    def update_edited_fact(self, edit_fact, orig_fact):
        self.controller.affirm(edit_fact is not orig_fact)
        self.controller.affirm((orig_fact == 0) or (edit_fact.pk == orig_fact.pk))
        if edit_fact.dirty:
            # Update or add reference to latest edit.
            self.edit_facts[edit_fact.pk] = edit_fact
        elif orig_fact != 0:
            self.controller.affirm(not orig_fact.dirty)
            try:
                # Forget edited fact that's no longer different than orig.
                self.edit_facts.pop(orig_fact.pk)  # Ignoring: popped fact.
            except KeyError:
                pass

    # ***

    def stand_up(self):
        def _standup():
            ensure_backed_up()
            assert len(self.conjoined.groups) > 0
            assert len(self.conjoined.groups[0]) > 0
            ensure_view_facts()
            self.conjoined.place_time_rifts()
            self.curr_fact = self.conjoined.find_first_dirty()

        def ensure_backed_up():
            # Create a just-in-case backup file to capture unsaved edits. We'll
            # call periodically during editor session, and can start session by
            # calling it, too (stand_up is called at start of carousel.gallop).
            self.dirty_callback()

        def ensure_view_facts():
            """
            Ensure at least 1 fact is loaded, because
            there is no empty Carousel state!.
            """
            if len(list(self.conjoined.facts)):
                return
            at_least_load_latest_fact()

        def at_least_load_latest_fact():
            self.controller.affirm(len(self.conjoined.groups) == 0)
            latest_fact = self.controller.facts.antecedent(
                # Should not matter controller.store.now_tz_aware() vs. now
                # because this runs just once, on carousel.gallop startup.
                ref_time=self.controller.now,
            )
            self.controller.affirm(latest_fact is not None)
            latest_fact.orig_fact = 0
            # FIXME: When latest_fact is None => what's empty carousel state?
            self.add_facts([latest_fact])

        _standup()

    # ***

    def toss_last_edit(self):
        undone = self.redo_undo.undo_last_edit(restore_facts=None)
        return undone

    def undo_last_edit(self):
        undone = self.redo_undo.undo_last_edit(self.restore_facts)
        return undone

    def redo_last_undo(self):
        redone = self.redo_undo.redo_last_undo(self.restore_facts)
        return redone

    def restore_facts(self, pristine, altered):
        # 2019-01-31: (lb): I think we can skip manage_edited_dirty_deleted
        # (managing 'interval-gap') because that's encoded in redo-undo Facts.

        for edit_fact in pristine:
            self.controller.affirm(edit_fact.orig_fact.pk != 0)
            self.update_edited_fact(edit_fact, edit_fact.orig_fact)

        self.conjoined.apply_edits(edit_facts=pristine, last_edits=altered)
        # Jump to the "main" Fact that was edited.
        self.curr_fact = self.conjoined.locate_wired(pristine[0])
        self.dirty_callback()

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
        pasted_what = self.clipboard.paste_copied_meta(
            edit_fact, reset_fact=self.reset_copied_meta,
        )
        self.apply_edits(edit_fact)

        return pasted_what

    def reset_copied_meta(self, edit_fact):
        # The clipboard has a cycle mechanism (self.clipboard.paste_cnt) that
        # cycles over different attributes to paste as the user repeats the
        # same command. E.g., first press pastes activity. Next press pastes
        # the tags. Third pastes description. And fourth pastes everything.
        # Between each paste, the fact is reset, so only one attribute gets
        # changed, and there's only one undo item created.

        # The first undo is the one we created in paste_copied_meta.
        _latest_changes = self.redo_undo.undo.pop()
        self.controller.affirm(len(_latest_changes.pristine) == 1)
        self.controller.affirm(_latest_changes.pristine[0] == edit_fact)

        # The second undo is the one created the last time this method called.
        before_paste = self.redo_undo.undo.pop()
        self.controller.affirm(len(before_paste.pristine) == 1)

        # Reset edit_fact in place.
        restore_fact = before_paste.pristine[0]
        edit_fact.activity = restore_fact.activity
        edit_fact.tags = restore_fact.tags
        edit_fact.description = restore_fact.description
        self.controller.affirm(edit_fact.orig_fact)

        # Start a new undo (sets UndoRedoTuple.pristine with copy of edit_fact).
        self.redo_undo.add_undoable([edit_fact.copy()], before_paste.what)
        # EditManager.paste_copied_meta calls its apply_edits after
        # calling this method, which ensures UndoRedoTuple.altered is set.

    # ***

    def paste_factoid(self, factoid):
        def _paste_factoid():
            try:
                user_fact = parse_factoid()
            except Exception as err:
                return False, str(err)
            else:
                if not apply_changes(user_fact):
                    return False, None
                return True, None

        def parse_factoid():
            user_fact = must_create_fact_from_factoid(
                self.controller, factoid, time_hint='verify_none',
            )
            return user_fact

        def apply_changes(user_fact):
            edit_fact = self.editable_fact()
            if not verify_differences(user_fact, edit_fact):
                return False
            apply_edits(user_fact, edit_fact)
            return True

        def verify_differences(user_fact, edit_fact):
            # The Factoid's PKs are all None, so a direct == won't work. Also, time
            # wouldn't match. Which is also why as_tuple(include_pk=False) won't work.
            if (
                True
                and edit_fact.activity.equal_fields(user_fact.activity)
                and set(tag_names(edit_fact)) == set(tag_names(user_fact))
                and edit_fact.description == user_fact.description
            ):
                return False
            return True

        # We can just compare tag names and not call tag.as_tuple(include_pk=False)
        # to compare the two Facts. (Tag has 'deleted' and 'hidden', but both have
        # been abandoned -- there's no way to 'delete' a tag, rather, just remove it
        # from all Facts; and 'hidden' was added to the front end where it belongs.)
        def tag_names(fact):
            return [tag.name for tag in fact.tags]

        def apply_edits(user_fact, edit_fact):
            self.undoable_editable_fact(what='paste-factoid', edit_fact=edit_fact)
            if not edit_fact.activity.equal_fields(user_fact.activity):
                edit_fact.activity = user_fact.activity
            # Send new tag name strings to rags_replace, so it'll look through
            # the Fact's existing tags for a matching tag (and its Tag object).
            edit_fact.tags_replace(edit_fact.tags + tag_names(user_fact))
            # We could append description if one already exists, but seems more
            # logical to not add description if already there.
            if not edit_fact.description and user_fact.description:
                edit_fact.description = user_fact.description
            self.apply_edits(edit_fact)

        return _paste_factoid()

    # ***

    def edit_time_adjust(self, *args, **kwargs):
        self.time_edit.edit_time_adjust(*args, **kwargs)

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

    def jump_fact_dec(self, count=1):
        """"""
        for idx in range(count):
            prev_fact = self.conjoined.jump_fact_dec()
            if prev_fact is None:
                return prev_fact
            elif prev_fact.dirty:
                self.update_edited_fact(prev_fact, prev_fact.orig_fact)
        return prev_fact

    def jump_fact_inc(self, count=1):
        """"""
        for idx in range(count):
            next_fact = self.conjoined.jump_fact_inc()
            if next_fact is None:
                return next_fact
            elif next_fact.dirty:
                self.update_edited_fact(next_fact, next_fact.orig_fact)
        return next_fact

    # ***

    def jump_day_dec(self, days=1):
        """"""
        return self.conjoined.jump_day_dec(days=days)

    def jump_day_inc(self, days=1):
        """"""
        return self.conjoined.jump_day_inc(days=days)

    # ***

    def jump_rift_dec(self):
        """"""
        self.conjoined.jump_rift_dec()

    def jump_rift_inc(self):
        """"""
        self.conjoined.jump_rift_inc()

    # ***

    def jump_fact_first(self):
        """"""
        self.conjoined.jump_fact_first()

    def jump_fact_final(self):
        """"""
        self.conjoined.jump_fact_final()

    # ***

    def save_edited_facts(self):
        """"""
        # 2019-01-23 22:28: (lb): I wrote this quick in the past hour.
        # Seems to work. Guess we'll see how stable it is!

        def _save_edited_facts():
            curr_fact = self.curr_fact
            # 2019-01-23 20:46: Just assume the Carousel handled conflicts?
            # LATER/BACKLOG: What about if store changed in background?
            #   - Or would changed Facts have PK marked deleted?
            #     Would error propagate on changed db?
            edited_facts = self.prepared_facts
            ignore_pks = [fact.pk for fact in edited_facts]
            keep_fact, saved_facts = save_edited_trustworthy(
                edited_facts, ignore_pks,
            )
            keep_fact = reset_editing(keep_fact, saved_facts, curr_fact)
            # Return fact for zone_manager to jump to.
            return keep_fact, saved_facts

        def save_edited_trustworthy(edited_facts, ignore_pks):
            keep_fact = None
            saved_facts = []
            for edit_fact in edited_facts:
                new_fact = save_edited_fact(edit_fact, ignore_pks)
                if new_fact is None:
                    return save_edited_fact_failed()
                saved_facts.append(new_fact)
                if edit_fact is self.curr_fact:
                    keep_fact = new_fact
                affirm_saved_edited_fact(edit_fact, new_fact)
            return keep_fact, saved_facts

        def save_edited_fact_failed():
            # Something went wrong, and we displayed an error.
            # Return now, and leave the store in a Bad State.
            # Users are encouraged to keep their data stores
            # under revision control so that they can recover
            # from blunders such as these. And we should make
            # sure our code is tough and resilient and stable.
            # I.e., we don't need to bother handling this error
            # better; just don't cause an error.
            return None, None  # Short-circuit return!

        def save_edited_fact(edit_fact, ignore_pks):
            # (lb): SIMILAR: edits_manager.save_edited_fact, create.save_fact.
            if edit_fact.pk and edit_fact.pk < 0:
                edit_fact.pk = None
            if edit_fact.pk is None and edit_fact.deleted:
                self.controller.client_logger.debug(
                    'Deleted fact: {}'.format(edit_fact.short)
                )
                return []
            try:
                return self.controller.facts.save(
                    edit_fact, ignore_pks=ignore_pks,
                )
            except Exception as err:
                import traceback
                self.controller.client_logger.debug(traceback.format_exc())
                # A failure on a CLI command (without PPT interface) might do:
                #   import traceback
                #   traceback.print_exc()
                #   dob_in_user_exit(str(err))
                # But Carousel has a popup message handler.
                self.error_callback(errmsg='Failed to save fact!\n\n  “{}”'.format(err))
                return None

        def affirm_saved_edited_fact(edit_fact, new_fact):
            # (lb): It's easier to reset editing than to try to update state.
            #   So just a few affirmations, and then moving along.
            #   (The caller will return the saved curr_fact, and we'll
            #   rebuild the Carousel with that one Fact. Everything else
            #   will be rebuilt from scratch.)
            if edit_fact.pk:
                # PK is different for saved fact, and old fact is marked deleted;
                #   except for active (an ongoing) Fact, which retains its ID.
                if edit_fact.pk != new_fact.pk:
                    self.controller.affirm(new_fact.pk >= edit_fact.pk)
                    self.controller.affirm(edit_fact.deleted)
                else:
                    self.controller.affirm(not edit_fact.deleted)
                self.controller.affirm(self.edit_facts[edit_fact.pk] is edit_fact)
            else:
                # PK is None, so new Fact.
                self.controller.affirm(not edit_fact.deleted)
                self.controller.affirm(not new_fact.deleted)
                self.controller.affirm(new_fact.pk > 0)
            self.controller.affirm(new_fact.orig_fact is None)

        def reset_editing(keep_fact, saved_facts, curr_fact):
            if not saved_facts:
                return curr_fact
            if keep_fact is None:
                keep_fact = curr_fact
                curr_fact.orig_fact = None
                curr_fact.next_fact = None
                curr_fact.prev_fact = None
            # Because saving creates new Fact IDs, and because
            # it'd be a pain to update either all affected
            # Facts' IDs (think not only prepared_facts/conjoined.facts,
            # but also redo_undo.undo, redo_undo.redo, conjoined.by_pk,
            # and most importantly, all the Facts' next_fact and prev_fact
            # pointers!), reset every place that has a reference to any
            # Facts.
            # See also: self.setup_edit_help()
            keep_fact.orig_fact = None
            keep_fact.next_fact = None
            keep_fact.prev_fact = None
            self.setup_editing(edit_facts=[keep_fact], orig_facts=[])
            self.curr_fact = keep_fact
            return keep_fact

        return _save_edited_facts()

