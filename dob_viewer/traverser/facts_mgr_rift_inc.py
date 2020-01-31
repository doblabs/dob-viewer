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

"""FactsManager_RiftInc"""

__all__ = (
    'FactsManager_RiftInc',
)


class FactsManager_RiftInc(object):
    """"""
    def jump_rift_inc(self):
        """"""
        def _jump_rift_inc():
            next_fact = self.find_rift_fact(is_next=True)
            if next_fact is None:
                _final_group, final_fact = group_latest(ceil_groups())
                next_fact = final_fact
                self.fulfill_jump(next_fact, reason='rift-inc')
            return next_fact

        def ceil_groups():
            if (
                (self.curr_group is self.groups[0])
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
                    (len(self.groups) > 1)
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
            if final_group.until_time_stops:
                # Look no further! (To test: press `G` a bunch.)
                return final_group, final_fact
            self.controller.affirm(final_fact.next_fact is None)
            latest_fact = self.controller.find_latest_fact()
            if not latest_fact:
                self.controller.affirm(final_fact.unstored)
            else:
                try:
                    latest_fact = self.by_pk[latest_fact.pk]
                    self.controller.affirm(latest_fact.orig_fact is not None)
                except KeyError:
                    self.controller.affirm(latest_fact.orig_fact is None)
                    latest_fact.orig_fact = 0
                    self.add_facts([latest_fact])
            if (
                (not latest_fact)
                or (latest_fact.deleted)
                or (latest_fact.pk == final_fact.pk)
                or (latest_fact < final_fact)
            ):
                return final_group, final_fact
            # If the new_facts were after latest_fact, we'll have loaded
            # latest_fact, but we'll be showing the final new, next Fact.
            final_group = self.groups[-1]
            latest_fact = final_group[-1]
            return final_group, latest_fact

        return _jump_rift_inc()

