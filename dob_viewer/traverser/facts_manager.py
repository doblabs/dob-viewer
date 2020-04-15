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

"""Facts Carousel"""

from contextlib import contextmanager

from sortedcontainers import SortedKeyList

from .facts_mgr_fact_dec import FactsManager_FactDec
from .facts_mgr_fact_inc import FactsManager_FactInc
from .facts_mgr_gap import FactsManager_Gap
from .facts_mgr_jump import FactsManager_Jump
from .facts_mgr_jump_time import FactsManager_JumpTime
from .facts_mgr_rift import FactsManager_Rift
from .facts_mgr_rift_dec import FactsManager_RiftDec
from .facts_mgr_rift_inc import FactsManager_RiftInc
from .group_chained import GroupChained

__all__ = (
    'FactsManager',
)


class FactsManager(
    FactsManager_FactDec,
    FactsManager_FactInc,
    FactsManager_Gap,
    FactsManager_Jump,
    FactsManager_JumpTime,
    FactsManager_Rift,
    FactsManager_RiftDec,
    FactsManager_RiftInc,
):
    """"""

    # ***

    def __init__(self, controller, on_insert_fact, on_jumped_fact, *args, **kwargs):
        super(FactsManager, self).__init__(controller, *args, **kwargs)

        self.controller = controller
        self.on_insert_fact = on_insert_fact
        self.on_jumped_fact = on_jumped_fact
        self.debug = controller.client_logger.debug
        self.groups = self.sorted_contiguous_facts_list()
        self.by_pk = {}
        self.last_fact_pk = 0
        self._curr_fact = None
        self.curr_group = None
        self.curr_index = None

    def sorted_contiguous_facts_list(self):
        sorted_contiguous_facts_list = SortedKeyList(
            key=lambda group_chained: (group_chained.sorty_times),
        )
        return sorted_contiguous_facts_list

    # ***

    @property
    def curr_fact(self):
        return self._curr_fact

    @curr_fact.setter
    def curr_fact(self, curr_fact):
        if self.curr_fact is curr_fact:
            return
        group, index = self.locate_fact(curr_fact)
        self._curr_fact = curr_fact
        self.curr_group = group
        self.curr_index = index
        # (lb): 2019-01-21: This seems unnecessary, but why not.
        #   "In the name of coveragggggggggge!!!!!!!"
        # 2019-01-23: Hahaha, it fired on self.curr_group.time_since not
        #   having been extended after collapse_group! Hooray, affirm usage!
        self.controller.affirm(self.curr_group.contains_fact_time([curr_fact]))

    def locate_fact(self, some_fact):
        inserts_at = self.groups.bisect_key_left(some_fact.sorty_times)
        if (
            (inserts_at < len(self.groups))
            and (self.groups[inserts_at])
            # (lb): 2019-01-31: We had been comparing PKs here:
            #   and (self.groups[inserts_at][0].pk == some_fact.pk)
            # but I'm pretty sure we want to check the time window.
            #  (Such glaring confidence, I know!)
            and (self.groups[inserts_at][0].sorty_times == some_fact.sorty_times)
        ):
            group = self.groups[inserts_at]
        else:
            group = self.groups[inserts_at - 1]
        # The index raises ValueError if the fact is not in the group.
        index = group.index(some_fact)
        return group, index

    def locate_wired(self, ref_fact):
        try:
            group, index = self.locate_fact(ref_fact)
        except KeyError:
            return None
        else:
            return group[index]

    # ***

    def __getitem__(self, key):
        if key == 0:
            return self.groups[0][0]
        elif key == -1:
            return self.groups[-1][-1]
        raise TypeError(
            "'{0}' object is not really subscriptable".format(type(self))
        )

    def __len__(self):
        return sum([len(group) for group in self.groups])

    @property
    def debug__str(self):
        return '  ' + '\n  '.join(
            ['#{:3}: {}'.format(idx, grp) for idx, grp in enumerate(self.groups)]
        )

    # ***

    def add_facts(self, facts):
        if not facts:
            return

        grouped_facts = []
        for fact in facts:
            self.controller.affirm(fact.pk not in self.by_pk.keys())
            self.by_pk[fact.pk] = fact
            grouped_facts.append(fact)
            # For creating new Facts.
            if fact.unstored:
                self.last_fact_pk = min(self.last_fact_pk, fact.pk)

        # FIXME/2019-12-06: (lb): Just testing. Remove affirm arg. later.
        # group = GroupChained(grouped_facts)
        group = GroupChained(grouped_facts, affirm=self.controller.affirm)
        self.groups.add(group)

        self.logger_debug_groups('add_facts', group=group)

    def claim_time_span(self, since, until):
        owning_group = None

        sorty_times = (since, since)

        inserts_at = self.groups.bisect_key_left(sorty_times)
        # Because bisect_key_left, either the start of the indexed
        # group matches, or the time falls before the group indexed.
        if inserts_at < len(self.groups):
            if since == self.groups[inserts_at].time_since:
                owning_group = self.groups[inserts_at]
            else:
                self.controller.affirm(since < self.groups[inserts_at].time_since)
        if (owning_group is None) and (inserts_at > 0):
            before_it = inserts_at - 1
            self.controller.affirm(since > self.groups[before_it].time_since)
            if since <= self.groups[before_it].time_until:
                owning_group = self.groups[before_it]
            # else, since is between 2 groups; until might extend
            # past 2nd of the groups, which we'll check for later.

        if inserts_at == 0:
            # Because bisect_key_left, leftmost group
            # only matches if start exactly matches.
            if since == self.groups[0][0].start:
                owning_group = self.groups[0]

        else:
            # Time span precedes all existing groups' spans.
            self.controller.affirm(since < self.groups[0].time_since)

        if owning_group is None:
            owning_group = GroupChained()

        with self.fact_group_rekeyed(owning_group):
            owning_group.claim_time_span(since, until)

    # ***

    def apply_edits(self, edit_facts, last_edits):
        group, _index = self.locate_fact(last_edits[0])

        with self.fact_group_rekeyed(group):

            # Clear time windows of edited facts, as times may have changed.
            for last_edit in last_edits:
                last_index = group.index(last_edit)
                group_fact = group.pop(last_index)
                # 2020-04-09: (lb): I had this affirm here:
                #   self.controller.affirm(group_fact == last_edit)
                # which meant to say that the Fact in the Fact Manager
                # group matches the most recent Fact edit, i.e., the
                # group fact has not been updated yet.
                # However, on time edit, the apply_edit_time_start/end
                # methods update the editable fact, but the editable
                # facts are also part of the Facts Manager groups. So
                # while group_fact.pk == last_edit.pk, other attrs might
                # now differ.
                self.controller.affirm(
                    (group_fact == last_edit) or (group_fact in edit_facts)
                )

                if group_fact.has_prev_fact:
                    group_fact.prev_fact.next_fact = None
                if group_fact.has_next_fact:
                    group_fact.next_fact.prev_fact = None

                group_fact.prev_fact = None
                group_fact.next_fact = None

                del self.by_pk[group_fact.pk]

            for edit_fact in edit_facts:
                # Rather than try to rewire the Facts, e.g., by calling
                #   self.new_fact_wire_links(edit_fact)
                # leave the Facts unwired, and let the normal _inc/_dec
                # navigation methods fix the wiring.
                edit_fact.next_fact = None
                edit_fact.prev_fact = None
                group.add(edit_fact)
                self.by_pk[edit_fact.pk] = edit_fact

    # ***

    @contextmanager
    def fact_group_rekeyed(self, group=None, group_index=None):
        # Ensures that self.groups._keys is up to date.

        # The group's facts order should not change, but the group's
        # key might change, if some_fact is being prepended to the
        # group, because self.curr_group.facts[0].sorty_times.
        # As such, remove and re-add the group, so that SortedKeyList
        # can update, e.g., self.groups._maxes is set when a group is
        # updated, so really a group is invariant once it's added to
        # the sorted list. (If we didn't re-add the group, things happen,
        # like, self.groups.index(self.curr_group) will not find the
        # group if its sorty_times < _maxes.)
        group = group or self.curr_group
        if group_index is None:
            # MAYBE/2019-01-21: self.groups.index will raise ValueError
            #  if you edited the first or final fact while the group is
            #  still part of the sorted_contiguous_facts_list() container.
            # This is not, like, a moral issue, or anything, but for the
            #  sake of our code, anything that changes the group should
            #  be aware of this.
            # However, if we find that maintaining the code as such starts
            #  to become painful -- should this dance become more difficult
            #  -- we could fallback and walk self.groups for an object match.
            try:
                group_index = self.groups.index(group)
            except ValueError:
                # MAYBE/2019-01-21: See long comment from a few lines back.
                #  Look for exact group object match (i.e., instead of using
                #  sorty_times value). This is because groups.index uses
                #  _maxes and compares key values, ignoring object identity.
                #   and group.sorty_times changes based on its facts, and
                #   when we extend the time window. (lb): Long comment....
                self.controller.affirm(False)  # Unexpected path, but may work:
                for idx, grp in enumerate(self.groups):
                    if grp is group:
                        group_index = idx
                        break
                if group_index is None:
                    raise

        if group_index is not None:
            # NOTE: Use pop(), specifying an index, rather than remove(),
            #       which uses a key value, because sorty_times might already
            #       be invalid.
            self.groups.pop(group_index)

        yield

        self.groups.add(group)

        self.logger_debug_groups('fact_group_rekeyed', group=group)

        # Caller is responsible for wiring prev/next references.

    def logger_debug_groups(self, whence='', group=None):
        group = group or self.curr_group
        self.debug(
            '{}\n- group.sorty_times: {}\n-    groups._maxes: {}'.format(
                whence,
                group and group.sorty_times or '<curr_group is None>',
                self.groups._maxes,
            )
        )
        self.debug('\n{}'.format(self.debug__str))

    def curr_group_add(self, some_fact):
        # The new fact is not yet wired.
        self.controller.affirm(some_fact.next_fact is None)
        self.controller.affirm(some_fact.prev_fact is None)
        # The new fact is not a known fact. (Because of groups'
        # time_since/time_until windows, we shouldn't find Facts
        # from the store amongst open time whose PKs we've seen.)
        self.controller.affirm(some_fact.pk not in self.by_pk.keys())
        self.new_fact_wire_links(some_fact)

        with self.fact_group_rekeyed():
            self.curr_group.add(some_fact)
            self.by_pk[some_fact.pk] = some_fact

    def new_fact_wire_links(self, some_fact):
        # 2019-02-13: (lb): Just a *momentaneous* FYI. (Feature should be all wired now.)
        if some_fact.start == some_fact.end:
            self.controller.client_logger.warning(
                'Found MOMENTANEOUS: {}'.format(some_fact.short),
            )

        if self.curr_fact.start == some_fact.end:
            self.controller.affirm(self.curr_fact.prev_fact is None)
            self.curr_fact.prev_fact = some_fact
            some_fact.next_fact = self.curr_fact
        if self.curr_fact.end == some_fact.start:
            self.controller.affirm(self.curr_fact.next_fact is None)
            self.curr_fact.next_fact = some_fact
            some_fact.prev_fact = self.curr_fact

    # ***

    @property
    def facts(self):
        for group in self.groups:
            for fact in group.facts:
                yield fact

    # ***

    def is_final_fact(self, edit_fact):
        group, index = self.locate_fact(edit_fact)
        if not group.until_time_stops:
            return False
        if not index == len(group) - 1:
            return False
        return True

    # ***

    def pop_final_gap_fact(self):
        final_fact = self[-1]
        if not final_fact.is_gap:
            return None
        group_fact = self.groups[-1].pop(-1)
        self.controller.affirm(group_fact is final_fact)
        return group_fact

