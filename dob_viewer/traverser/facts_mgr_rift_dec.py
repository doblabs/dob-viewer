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

"""FactsManager_RiftDec"""

__all__ = (
    'FactsManager_RiftDec',
)


class FactsManager_RiftDec(object):
    """"""
    def jump_rift_dec(self):
        """"""
        def _jump_rift_dec():
            prev_fact = self.find_rift_fact(is_prev=True)
            if prev_fact is None:
                _first_group, first_fact = group_oldest(floor_groups())
                prev_fact = first_fact
                self.fulfill_jump(prev_fact, reason='rift-dec')
            return prev_fact

        def floor_groups():
            if (
                (self.curr_group is self.groups[-1])
                and (self.curr_index > 0)
            ):
                # Looking at new, next Facts, and not the first new
                # Fact, so scroll back to the first new, next Fact.
                first_group = self.groups[-1]
            else:
                first_group = self.groups[0]
                # If new, prev Facts, scroll to oldest Fact, then to first
                # new, prev Fact. (Note: If there are new, prev Facts, the
                # oldest Fact is already established at self.groups[1][0].)
                if (
                    (self.curr_group is not self.groups[0])
                    and (
                        (self.curr_group is not self.groups[1])
                        or (self.curr_index > 0)
                    )
                ):
                    first_group = self.groups[1]
            return first_group

        def group_oldest(first_group):
            first_fact = first_group[0]
            if first_group is not self.groups[0]:
                return first_group, first_fact
            if first_group.since_time_began:
                # Look no further! (To test: press `gg` a bunch.)
                return first_group, first_fact
            self.controller.affirm(first_fact.prev_fact is None)
            oldest_fact = self.controller.find_oldest_fact()
            if not oldest_fact:
                self.controller.affirm(first_fact.unstored)
            else:
                try:
                    oldest_fact = self.by_pk[oldest_fact.pk]
                    self.controller.affirm(oldest_fact.orig_fact is not None)
                except KeyError:
                    self.controller.affirm(oldest_fact.orig_fact is None)
                    oldest_fact.orig_fact = 0
                    self.add_facts([oldest_fact])
            if (
                (not oldest_fact)
                or (oldest_fact.deleted)
                or (oldest_fact.pk == first_fact.pk)
                or (oldest_fact > first_fact)
            ):
                return first_group, first_fact
            # If the new_facts were before oldest_fact, we'll have loaded
            # oldest_fact, but we'll be showing the first new, prev Fact.
            first_group = self.groups[0]
            first_fact = first_group[0]
            return first_group, first_fact

        return _jump_rift_dec()

