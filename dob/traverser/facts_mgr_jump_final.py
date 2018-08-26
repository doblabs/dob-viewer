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
"""FactsManager_JumpFinal"""

from __future__ import absolute_import, unicode_literals

from ..cmds_list.fact import find_latest_fact

__all__ = [
    'FactsManager_JumpFinal',
]


class FactsManager_JumpFinal(object):
    """"""
    def scroll_fact_last(self):
        """"""
        def _facts_mgr_jump_final():
            self.client_logger_state('jump-final-start')
            final_group, final_fact = group_latest(ceil_groups())
            self.controller.affirm(final_fact.next_fact in [None, -1])
            self._curr_fact = final_fact
            self.curr_group = final_group
            self.curr_index = len(self.groups[-1]) - 1
            self.controller.affirm(self.curr_index >= 0)
            self._jump_time_reference = None
            self.client_logger_state('jump-final-after')
            return final_fact

        def ceil_groups():
            if (
                (self.contains_new_prev_facts)
                and (self.curr_group is self.groups[0])
                and (self.curr_index < (len(self.groups[0]) - 1))
            ):
                # Looking at new, prev Facts, and not the final new
                # Fact, so scroll forward to the last new, prev Fact.
                final_group = self.groups[0]
            else:
                final_group = self.groups[-1]
                # If new, next Facts, scroll to latest Fact, then to final
                # new, next Fact.
                if (
                    (self.contains_new_next_facts)
                    and (len(self.groups) > 1)
                    and (
                        (self.curr_group is not self.groups[-1])
                        and (
                            (self.curr_group is not self.groups[-2])
                            or (self.curr_index < (len(self.groups[-2]) - 1))
                        )
                    )
                ):
                    final_group = self.groups[-2]
            return final_group

        def group_latest(final_group):
            final_fact = final_group[-1]
            if final_group is not self.groups[-1]:
                return final_group, final_fact
            if final_fact.next_fact is -1:
                return final_group, final_fact
            self.controller.affirm(final_fact.next_fact is None)
            latest_fact = find_latest_fact(self.controller)
            if not latest_fact:
                self.controller.affirm(final_fact.unstored)
            else:
                try:
                    latest_fact = self.by_pk[latest_fact.pk]
                    self.controller.affirm(latest_fact.orig_fact is not None)
                except KeyError:
                    self.controller.affirm(latest_fact.orig_fact is None)
                    latest_fact.orig_fact = latest_fact
                    self.add_facts([latest_fact])
            if (
                (not latest_fact)
                or (latest_fact.deleted)
                or (latest_fact.pk == final_fact.pk)
                or (latest_fact < final_fact)
            ):
                final_fact.next_fact = -1  # No more later Facts!
                return final_group, final_fact
            latest_fact.next_fact = -1
            # If the new_facts were after latest_fact, we'll have
            # loaded latest_fact, but we'll be showing the final
            # new, next Fact.
            final_group = self.groups[-1]
            latest_fact = final_group[-1]
            latest_fact.next_fact = -1
            return final_group, latest_fact

        return _facts_mgr_jump_final()

