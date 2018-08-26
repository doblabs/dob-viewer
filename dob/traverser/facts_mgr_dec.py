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
"""FactsManager_Decrementer"""

from __future__ import absolute_import, unicode_literals

import datetime

__all__ = [
    'FactsManager_Decrementer',
]


class FactsManager_Decrementer(object):
    """"""
    def decrement(self):
        """"""
        def _decrement():
            prev_fact = fetch_prev_fact()
            if prev_fact is None:
                self.curr_fact.prev_fact = -1
            prev_fact = maybe_fill_gap(prev_fact)
            if prev_fact is None:
                return None
            self.controller.affirm(self.curr_fact > prev_fact)
            self.curr_fact = prev_fact
            self._jump_time_reference = None
            self.client_logger_state('decrement')
            return prev_fact

        def fetch_prev_fact():
            if self.curr_fact.prev_fact is -1:
                # prev_fact is -1 when it's first known fact, either in a
                # group of new Facts, or in group of Facts found in store.
                self.controller.affirm(self.curr_index == 0)
                return fetch_final_from_prev_group()
            elif self.curr_fact.prev_fact is not None:
                # prev_fact points to an actual Fact, which is the following
                # Fact in the current group.
                self.controller.affirm(self.curr_index > 0)
                return fetch_prev_from_curr_group_redux()
            else:
                # prev_fact is None until we verify prev fact.
                return fetch_prev_from_a_group_or_store()

        def fetch_final_from_prev_group():
            final_from_prev_group, prev_group_index = peek_final_from_prev_group()
            if final_from_prev_group is None:
                return None
            self.curr_group = self.groups[prev_group_index]
            self.curr_index = len(self.curr_group) - 1
            self.controller.affirm(final_from_prev_group is self.curr_group[-1])
            return final_from_prev_group

        def peek_final_from_prev_group():
            prev_fact = None
            prev_group_index = self.groups.index(self.curr_group) - 1
            if prev_group_index >= 0:
                prev_fact = self.groups[prev_group_index][-1]
            return prev_fact, prev_group_index

        def fetch_prev_from_curr_group_redux():
            self.curr_index -= 1
            prev_from_curr_group = self.curr_group[self.curr_index]
            self.controller.affirm(self.curr_fact.prev_fact is prev_from_curr_group)
            self.controller.affirm(prev_from_curr_group.next_fact is self.curr_fact)
            return prev_from_curr_group

        def fetch_prev_from_a_group_or_store():
            prev_from_store = fetch_prev_from_store()
            if self.curr_index > 0:
                return compare_curr_group_to_store(prev_from_store)
            else:
                return compare_prev_group_to_store(prev_from_store)

        def fetch_prev_from_store():
            prev_from_store = self.controller.facts.antecedent(self.curr_fact)
            if not prev_from_store:
                # On first fact.
                self.curr_fact.prev_fact = -1
                return None
            elif prev_from_store.pk in self.by_pk.keys():
                # Fact from store was previously added to the container.
                return None
            prev_from_store.orig_fact = prev_from_store
            return prev_from_store

        def compare_curr_group_to_store(prev_from_store):
            self.curr_index -= 1
            prev_from_curr_group = self.curr_group[self.curr_index]
            if prev_from_store and prev_from_store > prev_from_curr_group:
                prev_fact = curr_group_add_prev(prev_from_store)
                return prev_fact
            else:
                if prev_from_store:
                    self.add_facts([prev_from_store])
                # Leave: self.curr_index
                self.curr_fact.prev_fact = prev_from_curr_group
                prev_from_curr_group.next_fact = self.curr_fact
                return prev_from_curr_group

        def compare_prev_group_to_store(prev_from_store):
            final_from_prev_group, prev_group_index = peek_final_from_prev_group()
            if not prev_from_store and not final_from_prev_group:
                return None
            if final_from_prev_group and (
                (not prev_from_store) or (final_from_prev_group > prev_from_store)
            ):
                prev_fact = maybe_collapse_group(final_from_prev_group, prev_group_index)
                if prev_from_store:
                    self.add_facts([prev_from_store])
            else:
                prev_fact = curr_group_add_prev(prev_from_store)
            return prev_fact

        def maybe_collapse_group(prev_fact, prev_group_index):
            if prev_fact.unstored != self.curr_fact.unstored:
                self.curr_fact.prev_fact = -1
                self.curr_group = self.groups[prev_group_index]
                self.curr_index = len(self.curr_group) - 1
            else:
                if prev_fact.end == self.curr_fact.start:
                    self.curr_fact.prev_fact = prev_fact
                    prev_fact.next_fact = self.curr_fact
                prev_group = self.groups.pop(prev_group_index)
                group_index = self.groups.index(self.curr_group)
                # Note that addition order doesn't matter, because sorted.
                # So this:
                #  self.curr_group += prev_group
                # is basically same as this:
                #  self.curr_group[:] = prev_group + self.curr_group
                # where slice operator calls __setitem__ for each fact,
                # whereas addition calls __add__ or __radd__ just once.
                # But both probably call add() on each Fact; it's a wash.
                self.curr_group[:] = prev_group + self.curr_group
                # Leave at 0: self.curr_index
                self.curr_group_update_keys(group_index, prev_fact)
            self.controller.affirm(self.curr_group[self.curr_index] is prev_fact)
            return prev_fact

        def curr_group_add_prev(prev_fact):
            self.controller.affirm(self.curr_fact.prev_fact is None)
            if prev_fact.end == self.curr_fact.start:
                self.curr_fact.prev_fact = prev_fact
                prev_fact.next_fact = self.curr_fact
            self.curr_group_add(prev_fact)
            # Leave: self.curr_index.
            self.controller.affirm(
                self.curr_group[self.curr_index] is prev_fact
            )
            return prev_fact

        def maybe_fill_gap(prev_fact):
            # FIXME/2018-07-02: (lb): Make interval gap config'able?
            gap_fact = None
            if prev_fact is None:
                self.controller.affirm(self.curr_fact.prev_fact is -1)
                # FIXME/2018-07-31 11:35: Make user_start_time configable.
                user_start_time = datetime.datetime(1977, 6, 12, 23, 14)
                if self.curr_fact.start > user_start_time:
                    gap_fact = self.fact_from_interval_gap(
                        user_start_time, self.curr_fact.start,
                    )
            elif prev_fact.end != self.curr_fact.start:
                self.controller.affirm(self.curr_fact.prev_fact is None)
                gap_fact = self.fact_from_interval_gap(
                    prev_fact.end, self.curr_fact.start,
                )
            if gap_fact is None:
                return prev_fact
            self.insert_gap_prev(gap_fact)
            return gap_fact

        return _decrement()

