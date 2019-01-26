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

from datetime import timedelta
from math import inf

__all__ = [
    'FactsManager_JumpDay',
]


class FactsManager_JumpDay(object):
    """"""
    @property
    def jump_time_reference(self):
        if not self._jump_time_reference:
            self.jump_time_reference = self.curr_fact.start
        return self._jump_time_reference

    @jump_time_reference.setter
    def jump_time_reference(self, jump_time_reference):
        self._jump_time_reference = jump_time_reference

    # ***

    def decrement_one_day(self):
        prev_day = self.jump_time_reference - timedelta(days=1)
        prev_fact = self.jump_to_fact_nearest(
            prev_day, until=prev_day, sort_order='desc',
        )
        return prev_fact

    def increment_one_day(self):
        next_day = self.jump_time_reference + timedelta(days=1)
        next_fact = self.jump_to_fact_nearest(
            next_day, since=next_day, sort_order='asc',
        )
        return next_fact

    # ***

    def jump_to_fact_nearest(self, ref_time, sort_order, **kwargs):
        """"""
        def _jump_to_fact_nearest():
            was_fact = self.curr_fact

            fact_from_store = nearest_fact_from_store()

            fact_from_group = nearest_fact_from_group()

            return choose_nearest_fact(fact_from_store, fact_from_group, was_fact)

        def nearest_fact_from_store():
            facts_from_store = self.controller.facts.surrounding(
                ref_time, inclusive=True,
            )
            if self.curr_fact.pk in [fact.pk for fact in facts_from_store]:
                if sort_order == 'desc':
                    fact_from_store = self.controller.facts.antecedent(self.curr_fact)
                else:
                    fact_from_store = self.controller.facts.subsequent(self.curr_fact)
            elif facts_from_store:
                fact_from_store = facts_from_store[0]
            else:
                facts_from_store = self.controller.facts.get_all(
                    partial=True,
                    limit=1,
                    sort_col='start',
                    sort_order=sort_order,
                    **kwargs  # I.e., since= or until=.
                )
                fact_from_store = facts_from_store[0] if facts_from_store else None
            if fact_from_store is not None:
                fact_from_store.orig_fact = fact_from_store
            return fact_from_store

        def nearest_fact_from_group():
            fact_from_group = None
            sorty_tuple = (ref_time, ref_time, -inf)
            insert_at = self.groups.bisect_key_left(sorty_tuple)
            if insert_at < len(self.groups):
                fact_group = self.groups[insert_at]
                cmp_fact = fact_group[0]
                if (
                    (cmp_fact.start <= ref_time)
                    and ((not cmp_fact.end) or (cmp_fact.end >= ref_time))
                ):
                    fact_from_group = cmp_fact
            if (fact_from_group is None) and (insert_at > 0):
                fact_group = self.groups[insert_at - 1]
                fact_index = fact_group.bisect_key_left(sorty_tuple)
                if fact_index == 0:
                    fact_from_group = fact_group[0]
                else:
                    fact_from_group = fact_group[fact_index - 1]
            if (not fact_from_group) or (fact_from_group.pk == self.curr_fact.pk):
                return None
            return fact_from_group

        def choose_nearest_fact(fact_from_store, fact_from_group, was_fact):
            if (not fact_from_store) and (not fact_from_group):
                return None

            if (
                (not fact_from_group)
                or (
                    fact_from_store
                    and (
                        (
                            (sort_order == 'desc')
                            and (fact_from_store < fact_from_group)
                        )
                        or (
                            (sort_order == 'asc')
                            and (fact_from_store > fact_from_group)
                        )
                    )
                )
            ):
                nearest_fact = fact_from_store
            else:
                nearest_fact = fact_from_group

            if nearest_fact.pk not in self.by_pk.keys():
                self.add_facts([nearest_fact])

            self.curr_fact = nearest_fact

            adj_time = ref_time
            if sort_order == 'desc':
                while self.curr_fact.end and (self.curr_fact.end < adj_time):
                    adj_time -= timedelta(days=1)
            else:
                self.controller.affirm(sort_order == 'asc')
                while self.curr_fact.start > adj_time:
                    adj_time += timedelta(days=1)

            self.jump_time_reference = adj_time

            return nearest_fact

        return _jump_to_fact_nearest()

