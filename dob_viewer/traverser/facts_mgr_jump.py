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

""""""

from nark.items.fact import UntilTimeStops

__all__ = (
    'FactsManager_Jump',
)


class FactsManager_Jump(object):
    """"""

    # ***

    def fulfill_jump(self, jump_fact, reason=''):
        # Caller will have updated curr_group and curr_index, if necessary.
        # Note that we do not set FactsManager self.curr_fact directly,
        # but call a shim function so EditsManager can react, too.
        #   self.curr_fact = jump_fact
        self.on_jumped_fact(jump_fact)
        self._jump_time_reference = None
        self.debug_log_facts_mgr_state(reason)

    # ***

    def debug_log_facts_mgr_state(self, caller_name):
        self.debug(
            '{}: len(groups): {} / curr_index: {}\n'
            '- grps:\n{}\n- cgrp: {}\n- curr: {}'
            .format(
                caller_name,
                len(self.groups),
                self.curr_index,
                self.debug__str,
                self.curr_group,
                self.curr_fact.short,
            )
        )

    # ***

    def jump_to_fact_nearest(self, since_time=None, until_time=None):
        """"""
        def _jump_to_fact_nearest():
            assert (since_time is not None) ^ (until_time is not None)
            ref_time = since_time or until_time
            fact_group, group_fact, is_perfect = find_nearest_group_fact(ref_time)
            store_fact = is_perfect and None or find_nearest_store_fact(ref_time)
            nearest_fact = choose_nearest(fact_group, group_fact, store_fact)
            debug_log_chosen_fact(
                ref_time, nearest_fact, fact_group, group_fact, store_fact,
            )

            if nearest_fact is not None:
                if nearest_fact.pk not in self.by_pk.keys():
                    self.add_facts([nearest_fact])
                reason = 'jump-{}'.format('next' if since_time else 'prev')
                self.fulfill_jump(nearest_fact, reason=reason)
            update_time_reference(ref_time)

            return nearest_fact

    # ***

        def find_nearest_group_fact(ref_time):
            # Find the group index nearest ref_time. We use UntilTimeStops
            # so the index is 1 greater than group index for most matches
            # (all except the final ongoing (active) fact group).
            sorty_times = (ref_time, UntilTimeStops)
            inserts_at = self.groups.bisect_key_left(sorty_times)

            # Check for ongoing (active) fact group.
            if inserts_at == (len(self.groups) - 1):
                if sorty_times == self.groups[-1].sorty_times:
                    return self.groups[-1], self.groups[-1][0], True

            # If inserts_at is 0, ref_time is before any group's since_time,
            # or there's only one group and it's ongoing (active).
            if inserts_at == 0:
                first_group = self.groups[0]
                if ref_time == first_group.time_since:
                    return first_group, first_group[0], True
                elif since_time is not None:
                    # Momentum is forward, so grab first group's fact;
                    # and return False, so caller knows to look in store
                    # and decide between the two.
                    return first_group, first_group[0], False
                else:
                    # Momentum is backward in time, and there's nothing there.
                    return first_group, None, False

            try_group = self.groups[inserts_at - 1]
            self.controller.affirm(ref_time >= try_group.time_since)
            self.controller.affirm(sorty_times != try_group.sorty_times)

            # Check whether within group time window.
            if ref_time <= try_group.time_until:
                fact_index = try_group.bisect_key_left(sorty_times)
                best_fact = match_group_later_index(try_group, fact_index, ref_time)
                return try_group, best_fact, True

            # Between groups. Use momentum to determine which Fact to return.
            if since_time is not None:
                # Going forward.
                if inserts_at < len(self.groups):
                    # More groups to come!
                    return self.groups[inserts_at], self.groups[inserts_at][0], False
                else:
                    # On last group.
                    return self.groups[-1], None, False
            # Going backward. And we already processed inserts_at == 0.
            self.controller.affirm(until_time is not None)
            return try_group, try_group[-1], False

        # ***

        def match_group_later_index(fact_group, fact_index, ref_time):
            if fact_index >= len(fact_group):
                # Falls on or after start of last fact in group, but before
                # end of group time window, so use last fact of group.
                return fact_group[fact_index - 1]
            if fact_group[fact_index].start == ref_time:
                # Exact match. Use found fact.
                return fact_group[fact_index]
            # Falls before indicated fact.
            nearest_fact = fact_group[fact_index - 1]
            self.controller.affirm(nearest_fact.start <= ref_time)
            return nearest_fact

        # ***

        def find_nearest_store_fact(ref_time):
            if since_time is not None:
                return self.fetch_next_from_store(ref_time)
            else:
                return self.fetch_prev_from_store(ref_time)

        # ***

        def choose_nearest(fact_group, group_fact, store_fact):
            if group_fact is None:
                return choose_store_if_not_shadowed(fact_group, store_fact)
            if store_fact is None:
                return group_fact
            return prefer_store_then_group(fact_group, group_fact, store_fact)

        # ^^^

        def choose_store_if_not_shadowed(fact_group, store_fact):
            if store_fact is None:
                return None
            if since_time is not None:
                return store_if_not_shadowed_since(fact_group, None, store_fact)
            return store_if_not_shadowed_until(fact_group, None, store_fact)

        # ^^^

        def prefer_store_then_group(fact_group, group_fact, store_fact):
            if since_time is not None:
                return store_if_not_shadowed_until(fact_group, group_fact, store_fact)
            return store_if_not_shadowed_since(fact_group, group_fact, store_fact)

        # ^^^

        def store_if_not_shadowed_since(fact_group, group_fact, store_fact):
            if fact_group.time_until < store_fact.start:
                return store_fact
            return group_fact

        def store_if_not_shadowed_until(fact_group, group_fact, store_fact):
            store_fact_end = store_fact.end or UntilTimeStops
            if store_fact_end < fact_group.time_since:
                return store_fact
            return group_fact

        # ***

        def update_time_reference(ref_time):
            # Set the jump time reference.
            #
            # This function used to slide the time value further backward or
            # further forward to avoid the case where there's a Fact or Gap
            # longer than the jump time. In this case, as the user continues to
            # jump backward (or forward), they would keep seeing the same Fact.
            # - (lb): I had logic here that would sit in a while loop and adjust
            #   ref_time backward or forward by 1 day until the time reference
            #   was such that it would show a different Fact the next time the
            #   user jumped. But then I added the *count* feature, which allows
            #   users to jump by multiple days. And then this logic -- which did
            #   not feel well writ to begin with -- became untenable, given that
            #   the jump amount is no longer predictable.
            # E.g., consider the current Fact is the active Fact, now time is
            # 2020-04-12 09:30, and the user presses `5J` to go back five days,
            # ideally to 2020-04-07 09:30. Consider there's a Fact or Gap from
            # 2020-03-01 to 2020-04-07. Then the next `5J` will try
            # 2020-04-02 09:30, and the `5J` after that will try
            # 2020-03-28 09:30, etc. On each jump, the user sees the same Fact.
            # - (lb): So you can see how I wanted to make a better UX. However,
            #   in addition to the concerns mentioned above, there's another one.
            #   If we change the reference time, then operations are not
            #   transitive, e.g., user cannot `5J` from Fact A to B, and then
            #   run `5K` to return to Fact A.
            # - (lb): I think I've been able to solve this stumper by updating
            #   the bottom area Status message when the user jumps to show how
            #   many *days* the user jumped, and to also show the current
            #   reference time. That way, even if the current Fact does not
            #   change, the Status message will show something unique each
            #   time.
            self.jump_time_reference = ref_time

        # ***

        def debug_log_chosen_fact(
            ref_time, nearest_fact, fact_group, group_fact, store_fact,
        ):
            self.debug('ref_time: {}'.format(ref_time))
            self.debug(
                'near_group: {}'.format(fact_group.sorty_times)
            )
            self.debug(
                'nerst_fact: {}'.format(nearest_fact and nearest_fact.short)
            )
            self.debug(
                'group_fact: {}'.format(group_fact and group_fact.short)
            )
            self.debug(
                'store_fact: {}'.format(store_fact and store_fact.short)
            )
            if nearest_fact is None:
                chosen_from = 'neither'
            elif nearest_fact is group_fact:
                chosen_from = 'group'
            elif nearest_fact is store_fact:
                chosen_from = 'store'
            else:
                chosen_from = 'heh?'
            self.debug('- fact chosen from: {}'.format(chosen_from))

        # ***

        return _jump_to_fact_nearest()

