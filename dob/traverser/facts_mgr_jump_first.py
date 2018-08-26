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
"""FactsManager_JumpFirst"""

from __future__ import absolute_import, unicode_literals

from ..cmds_list.fact import find_maiden_fact

__all__ = [
    'FactsManager_JumpFirst',
]


class FactsManager_JumpFirst(object):
    """"""
    def scroll_fact_first(self):
        """"""
        def _facts_mgr_jump_first():
            self.client_logger_state('jump-first-start')
            first_group, first_fact = group_maiden(floor_groups())
            self.controller.affirm(first_fact.prev_fact in [None, -1])
            self._curr_fact = first_fact
            self.curr_group = first_group
            self.curr_index = 0
            self._jump_time_reference = None
            self.client_logger_state('jump-first-after')
            return first_fact

        def floor_groups():
            if (
                (self.contains_new_next_facts)
                and (self.curr_group is self.groups[-1])
                and (self.curr_index > 0)
            ):
                # Looking at new, next Facts, and not the first new
                # Fact, so scroll back to the first new, next Fact.
                first_group = self.groups[-1]
            else:
                first_group = self.groups[0]
                # If new, prev Facts, scroll to maiden Fact, then to first
                # new, prev Fact. (Note: If there are new, prev Facts, the
                # maiden Fact is already established at self.groups[1][0].)
                if (
                    (self.contains_new_prev_facts)
                    and (
                        (self.curr_group is not self.groups[0])
                        and (
                            (self.curr_group is not self.groups[1])
                            or (self.curr_index > 0)
                        )
                    )
                ):
                    first_group = self.groups[1]
            return first_group

        def group_maiden(first_group):
            first_fact = first_group[0]
            if first_group is not self.groups[0]:
                return first_group, first_fact
            if first_fact.prev_fact is -1:
                return first_group, first_fact
            self.controller.affirm(first_fact.prev_fact is None)
            maiden_fact = find_maiden_fact(self.controller)
            if not maiden_fact:
                self.controller.affirm(first_fact.unstored)
            else:
                try:
                    maiden_fact = self.by_pk[maiden_fact.pk]
                    self.controller.affirm(maiden_fact.orig_fact is not None)
                except KeyError:
                    self.controller.affirm(maiden_fact.orig_fact is None)
                    maiden_fact.orig_fact = maiden_fact
                    self.add_facts([maiden_fact])
            if (
                (not maiden_fact)
                or (maiden_fact.deleted)
                or (maiden_fact.pk == first_fact.pk)
                or (maiden_fact > first_fact)
            ):
                first_fact.prev_fact = -1  # No more prior Facts!
                return first_group, first_fact
            maiden_fact.prev_fact = -1
            # If the new_facts were before maiden_fact, we'll have
            # loaded maiden_fact, but we'll be showing the first
            # new, prev Fact.
            first_group = self.groups[0]
            first_fact = first_group[0]
            first_fact.prev_fact = -1
            return first_group, first_fact

        return _facts_mgr_jump_first()

