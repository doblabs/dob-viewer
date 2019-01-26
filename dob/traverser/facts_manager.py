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
"""Facts Carousel"""

from __future__ import absolute_import, unicode_literals

from contextlib import contextmanager
from sortedcontainers import SortedKeyList

from .facts_mgr_fact_dec import FactsManager_FactDec
from .facts_mgr_fact_inc import FactsManager_FactInc
from .facts_mgr_gap import FactsManager_Gap
from .facts_mgr_jump import FactsManager_Jump
from .facts_mgr_jump_time import FactsManager_JumpTime
from .facts_mgr_rift import FactsManager_Rift
from .facts_mgr_rift_inc import FactsManager_RiftInc
from .facts_mgr_rift_dec import FactsManager_RiftDec
from .group_chained import GroupChained
from .placeable_fact import PlaceableFact

__all__ = [
    'FactsManager',
]


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

    def __init__(self, controller, on_jumped_fact, *args, **kwargs):
        super(FactsManager, self).__init__(controller, *args, **kwargs)

        self.controller = controller
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
            key=lambda group_chained: (group_chained.sorty_tuple),
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
        inserts_at = self.groups.bisect_key_left(some_fact.sorty_tuple)
        if (
            (inserts_at < len(self.groups))
            and (self.groups[inserts_at])
            and (self.groups[inserts_at][0].pk == some_fact.pk)
        ):
            group = self.groups[inserts_at]
        else:
            group = self.groups[inserts_at - 1]
        # The index raises ValueError if the fact is not in the group.
        index = group.index(some_fact)
        return group, index

    # ***

    def update_fact(self, some_fact):
        def _update_fact():
            group, index = self.locate_fact(some_fact)
            old_fact = group[index]
            group[index] = some_fact

            # Fix group sorty_tuple key.
            self.curr_group_update_keys(index, some_fact)
            rewire_links(old_fact)
            self.by_pk[some_fact.pk] = some_fact

            rewire_curr(old_fact, group, index)

        def rewire_links(old_fact):
            some_fact.prev_fact = old_fact.prev_fact
            some_fact.next_fact = old_fact.next_fact
            if old_fact.prev_fact is not None:
                old_fact.prev_fact.next_fact = some_fact
            if old_fact.next_fact is not None:
                old_fact.next_fact.prev_fact = some_fact

        def rewire_curr(old_fact, group, index):
            if self._curr_fact is old_fact:
                self._curr_fact = some_fact
                self.curr_group = group
                self.curr_index = index

        _update_fact()

    def factory_reset(self, fact_pk):
        some_fact = self.by_pk[fact_pk]
        some_fact.reset_orig()

    # ***

    def __getitem__(self, key):
        if key is 0:
            return self.groups[0][0]
        elif key is -1:
            return self.groups[-1][-1]
        raise TypeError(
            "'{0}' object is not really subscriptable".format(type(self))
        )

    def __len__(self):
        return sum([len(group) for group in self.groups])

    @property
    def debug__str(self):
        return '█→ ' + ' ←██→ '.join([str(group) for group in self.groups]) + ' ←█'

    # ***

    def add_facts(self, facts):
        if not facts:
            return
        old_facts = []
        new_facts = []
        for fact in facts:
            self.controller.affirm(fact.pk not in self.by_pk.keys())
            self.by_pk[fact.pk] = fact
            if not fact.unstored:
                old_facts.append(fact)
            else:
                new_facts.append(fact)
                # For creating new Facts.
                self.last_fact_pk = min(self.last_fact_pk, fact.pk)
        for facts in [new_facts, old_facts]:
            if not facts:
                continue
            group_chained = GroupChained(facts)
            self.groups.add(group_chained)
        return

    # ***

    @contextmanager
    def curr_group_rekeyed(self, group=None, group_index=None):
        # Ensures that self.groups._keys is up to date.

        # The group's facts order should not change, but the group's
        # key might change, if some_fact is being prepended to the
        # group, because self.curr_group.facts[0].sorty_tuple.
        # As such, remove and re-add the group, so that SortedKeyList
        # can update, e.g., self.groups._maxes is set when a group is
        # updated, so really a group is invariant once it's added to
        # the sorted list. (If we didn't re-add the group, things happen,
        # like, self.groups.index(self.curr_group) will not find the
        # group if its sorty_tuple < _maxes.)
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
                #  sorty_tuple value). This is because groups.index uses
                #  _maxes and compares key values, ignoring object identity.
                #   and group.sorty_tuple changes based on its facts, and
                #   when we extend the time window. (lb): Log comment....
                self.controller.affirm(False)  # Unexpected path, but may work:
                for idx, grp in enumerate(self.groups):
                    if grp is group:
                        group_index = idx
                        break
                if group_index is None:
                    raise

        if group_index is not None:
            # NOTE: Use pop(), specifying an index, rather than remove(),
            #       which uses a key value, because sorty_tuple might already
            #       be invalid.
            self.groups.pop(group_index)

        yield

        self.groups.add(group)

        now_group_index = self.groups.index(group)
        self.controller.affirm(
            (group_index is None) or (group_index == now_group_index)
        )

        # Caller is responsible for wiring prev/next references.

        self.debug(
            '\n- group.sorty_tuple: {}\n-    groups._maxes: {}'.format(
                group.sorty_tuple, self.groups._maxes,
            )
        )

    def curr_group_add(self, some_fact):
        # Ensures that self.groups._keys is up to date.
        self.groups.remove(self.curr_group)
        self.curr_group.add(some_fact)
        self.by_pk[some_fact.pk] = some_fact
        self.groups.add(self.curr_group)

    def curr_group_update_keys(self, group_index, *facts):
        self.groups.pop(group_index)
        for some_fact in facts:
            self.by_pk[some_fact.pk] = some_fact
        self.groups.add(self.curr_group)

    @property
    def facts(self):
        for group in self.groups:
            for fact in group.facts:
                yield fact

    # ***

    @property
    def contains_new_next_facts(self):
        return self.groups[-1][0].unstored

    @property
    def contains_new_prev_facts(self):
        if len(self.groups) < 2:
            return False
        return self.groups[0][0].unstored

