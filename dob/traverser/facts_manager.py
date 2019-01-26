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

from sortedcontainers import SortedKeyList

from .facts_mgr_dec import FactsManager_Decrementer
from .facts_mgr_inc import FactsManager_Incrementer
from .facts_mgr_jump_day import FactsManager_JumpDay
from .facts_mgr_jump_final import FactsManager_JumpFinal
from .facts_mgr_jump_first import FactsManager_JumpFirst
from .group_chained import GroupChained
from .placeable_fact import PlaceableFact

__all__ = [
    'FactsManager',
]


class FactsManager(
    FactsManager_Decrementer,
    FactsManager_Incrementer,
    FactsManager_JumpDay,
    FactsManager_JumpFinal,
    FactsManager_JumpFirst,
):
    """"""

    # ***

    def __init__(self, controller):
        self.controller = controller
        self.groups = self.sorted_contiguous_facts_list()
        self.by_pk = {}
        self.last_fact_pk = 0

        self._curr_fact = None
        self.curr_group = None
        self.curr_index = None

        self.jump_time_reference = None

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
        self._jump_time_reference = None
        group, index = self.locate_fact(curr_fact)
        self._curr_fact = curr_fact
        self.curr_group = group
        self.curr_index = index

    def locate_fact(self, some_fact):
        insert_at = self.groups.bisect_key_left(some_fact.sorty_tuple)
        if (
            (insert_at < len(self.groups)) and
            (self.groups[insert_at][0].pk == some_fact.pk)
        ):
            group = self.groups[insert_at]
        else:
            group = self.groups[insert_at - 1]
        index = group.index(some_fact)
        return group, index

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

