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
        next_fact = self.find_rift_fact(is_next=True)
        if next_fact is None:
            return self.jump_to_latest_fact(reason='rift-inc')
        return next_fact

    def jump_fact_final(self, reason='fact-final'):
        """"""
        return self.jump_to_latest_fact(reason, include_edge_gap=True)

    # ***

    def jump_to_latest_fact(self, reason, include_edge_gap=False):
        """"""
        def _jump_to_latest_fact():
            final_group = self.groups[-1] if include_edge_gap else ceil_groups()
            _final_group, final_fact = group_latest(final_group)
            next_fact = final_fact
            # Set Edit/FactsManagers' curr_fact; Clear _jump_time_ref.;
            # Update viewed_fact_pks; Maybe call reset_paste/reset paste_cnt.
            self.fulfill_jump(next_fact, reason=reason)
            if include_edge_gap and next_fact.end is not None:
                # Create the active gap Fact.
                # - This'll happen if final Fact is complete: start dob (starts
                #   on final Fact), press 'left' 0 or more times, press 'G'.
                next_fact = self.jump_fact_inc()
                self.controller.affirm(next_fact.is_gap)
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
            # else, we're on the final group.
            elif final_group.until_time_stops:
                # The final_group's last element is the active Fact.
                # If it's a gap Fact, however, which is unsaved (contains
                # no user data), caller can opt to receive last real Fact.
                if not include_edge_gap and final_fact.is_gap:
                    # final_fact.is_gap, so try the second-to-last Fact.
                    # - This'll happen if last saved Fact is complete: start dob,
                    # press 'right' to create Gap fact, 'left', 'left', press 'f'
                    # to return to final true fact (find_rift_fact handles it),
                    # then press 'f' again, and the code will branch to here.
                    try:
                        final_fact = final_group[-2]
                    except IndexError:
                        # Well, at least we tried.
                        # (lb): I need to test this branch. Happens on empty db.
                        pass
                return final_group, final_fact
            self.controller.affirm(final_fact.next_fact is None)
            latest_fact = self.controller.find_latest_fact()
            if not latest_fact:
                # Empty database, meaning local Facts unsaved.
                self.controller.affirm(final_fact.unstored)
            else:
                try:
                    latest_fact = self.by_pk[latest_fact.pk]
                    self.controller.affirm(latest_fact.orig_fact is not None)
                except KeyError:
                    # The latest Fact from the db is new to us!
                    self.controller.affirm(latest_fact.orig_fact is None)
                    latest_fact.orig_fact = 0
                    self.add_facts([latest_fact])
            if (
                (not latest_fact)
                or (latest_fact.deleted)
                or (latest_fact.pk == final_fact.pk)
                or (latest_fact < final_fact)
            ):
                # The call above to find_latest_fact excluded deleted, so only
                # way latest_fact.deleted is if local copy in self.by_pk is so.
                return final_group, final_fact
            # If the new_facts were after latest_fact, we'll have loaded
            # latest_fact, but we'll be showing the final new, next Fact.
            final_group = self.groups[-1]
            latest_fact = final_group[-1]
            return final_group, latest_fact

        return _jump_to_latest_fact()

