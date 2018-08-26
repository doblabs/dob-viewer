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
"""FactsManager_Incrementer"""

from __future__ import absolute_import, unicode_literals

__all__ = [
    'FactsManager_Incrementer',
]


class FactsManager_Incrementer(object):
    """"""
    def increment(self):
        """"""
        def _increment():
            next_fact = fetch_next_fact()
            if next_fact is None:
                self.curr_fact.next_fact = -1
            next_fact = maybe_fill_gap(next_fact)
            if next_fact is None:
                return None
            self.controller.affirm(self.curr_fact < next_fact)
            self._curr_fact = next_fact
            self._jump_time_reference = None
            self.client_logger_state('increment')
            return next_fact

        def fetch_next_fact():
            if self.curr_fact.next_fact is -1:
                # next_fact is -1 when it's final known fact, either in a
                # group of new Facts, or in group of Facts found in store.
                self.controller.affirm((self.curr_index + 1) == len(self.curr_group))
                return fetch_first_from_next_group()
            elif self.curr_fact.next_fact is not None:
                # next_fact points to an actual Fact, which is the following
                # Fact in the current group.
                self.controller.affirm(self.curr_index < len(self.curr_group))
                return fetch_next_from_curr_group_redux()
            else:
                # next_fact is None until we verify next fact.
                return fetch_next_from_a_group_or_store()

        def fetch_first_from_next_group():
            first_from_next_group, next_group_index = peek_first_from_next_group()
            if first_from_next_group is None:
                return None
            self.curr_group = self.groups[next_group_index]
            self.curr_index = 0
            self.controller.affirm(first_from_next_group is self.curr_group[0])
            return first_from_next_group

        def peek_first_from_next_group():
            next_fact = None
            next_group_index = self.groups.index(self.curr_group) + 1
            if next_group_index < len(self.groups):
                next_fact = self.groups[next_group_index][0]
            return next_fact, next_group_index

        def fetch_next_from_curr_group_redux():
            self.curr_index += 1
            next_from_curr_group = self.curr_group[self.curr_index]
            self.controller.affirm(self.curr_fact.next_fact is next_from_curr_group)
            self.controller.affirm(next_from_curr_group.prev_fact is self.curr_fact)
            return next_from_curr_group

        def fetch_next_from_a_group_or_store():
            next_from_store = fetch_next_from_store()
            if (self.curr_index + 1) < len(self.curr_group):
                return compare_curr_group_to_store(next_from_store)
            else:
                return compare_next_group_to_store(next_from_store)

        def fetch_next_from_store():
            next_from_store = self.controller.facts.subsequent(self.curr_fact)
            if not next_from_store:
                # On final fact.
                self.curr_fact.next_fact = -1
                return None
            elif next_from_store.pk in self.by_pk.keys():
                # Fact from store was previously added to the container.
                return None
            next_from_store.orig_fact = next_from_store
            return next_from_store

        def compare_curr_group_to_store(next_from_store):
            next_from_curr_group = self.curr_group[self.curr_index + 1]
            if next_from_store and next_from_store < next_from_curr_group:
                next_fact = curr_group_add_next(next_from_store)
                return next_fact
            else:
                if next_from_store:
                    self.add_facts([next_from_store])
                self.curr_index += 1
                self.curr_fact.next_fact = next_from_curr_group
                next_from_curr_group.prev_fact = self.curr_fact
                return next_from_curr_group

        def compare_next_group_to_store(next_from_store):
            first_from_next_group, next_group_index = peek_first_from_next_group()
            if not next_from_store and not first_from_next_group:
                return None
            if first_from_next_group and (
                (not next_from_store) or (first_from_next_group < next_from_store)
            ):
                next_fact = maybe_collapse_group(first_from_next_group, next_group_index)
                if next_from_store:
                    self.add_facts([next_from_store])
            else:
                next_fact = curr_group_add_next(next_from_store)
            return next_fact

        def maybe_collapse_group(next_fact, next_group_index):
            if next_fact.unstored != self.curr_fact.unstored:
                self.curr_fact.next_fact = -1
                self.curr_group = self.groups[next_group_index]
                self.curr_index = 0
            else:
                if next_fact.start == self.curr_fact.end:
                    self.curr_fact.next_fact = next_fact
                    next_fact.prev_fact = self.curr_fact
                next_group = self.groups.pop(next_group_index)
                group_index = self.groups.index(self.curr_group)
                self.curr_group += next_group
                self.curr_index += 1
                self.curr_group_update_keys(group_index, next_fact)
            self.controller.affirm(self.curr_group[self.curr_index] is next_fact)
            return next_fact

        def curr_group_add_next(next_fact):
            self.controller.affirm(self.curr_fact.next_fact is None)
            if next_fact.start == self.curr_fact.end:
                self.curr_fact.next_fact = next_fact
                next_fact.prev_fact = self.curr_fact
            # (lb): Because sorting is based on curr_group[0], we don't need
            # to re-sort self.groups, but might as well, to be consistent.
            self.curr_group_add(next_fact)
            self.curr_index += 1
            self.controller.affirm(
                self.curr_group[self.curr_index] is next_fact
            )
            return next_fact

        def maybe_fill_gap(next_fact):
            gap_fact = None
            if next_fact is None:
                self.controller.affirm(self.curr_fact.next_fact is -1)
                if self.curr_fact.end is not None:
                    gap_fact = self.fact_from_interval_gap(
                        self.curr_fact.end, None,
                    )
            elif self.curr_fact.end != next_fact.start:
                self.controller.affirm(self.curr_fact.next_fact is None)
                gap_fact = self.fact_from_interval_gap(
                    self.curr_fact.end, next_fact.start,
                )
            if gap_fact is None:
                return next_fact
            self.insert_gap_next(gap_fact)
            return gap_fact

        return _increment()

