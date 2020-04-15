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

"""FactsManager_FactDec"""

import datetime

from nark.items.fact import SinceTimeBegan

__all__ = (
    'FactsManager_FactDec',
)


JULIAN_YEAR = datetime.timedelta(days=365, hours=6)  # 365.25 days, 31557600 secs.


# SYNC_ME: Keep FactsManager_FactDec and FactsManager_FactInc synced.
#   That, or write a generic base class, but that sounds painfuller to maintain.
#   then simply running meld as necessary:
#
#       meld facts_mgr_fact_dec.py facts_mgr_fact_inc.py &
class FactsManager_FactDec(object):
    """"""
    def __init__(self, controller, *args, **kwargs):
        super(FactsManager_FactDec, self).__init__()
        # FIXME/2018-07-31: Make user_start_time (beginning_of_time) configurable.
        #   E.g., user could set their birthday (birthtime).
        #   Could also maybe not use default if feature not enabled,
        #     but for now, using 100 yrs. ago.
        self.beginning_of_time = controller.now - (100 * JULIAN_YEAR)

    def jump_fact_dec(self):
        """"""
        def _jump_fact_dec():
            # Check first if we've reached the beginning of time.
            is_first_fact = (self.curr_index == 0)
            if is_first_fact and self.curr_group.since_time_began:
                return None
            # Each facts group represents a contiguous block of time that is
            # being managed by dob, and to ignore anything in the store from
            # that time. Find either the previous fact under dob's control,
            # or one from the store (that we'll wire into dob in a later step).
            prev_fact = fetch_prev_fact()
            # Each fact's prev_fact and next_fact links are not wired until
            # we inspect them here for gaps -- meaning, we fill in the gap facts
            # reactively, as the user traverses the facts in the carousel. Now.
            prev_fact = fill_gap_since(prev_fact)
            # If we've reached the beginning of time, there's nothing previous.
            if prev_fact is None:
                return None
            # Just a sanity check. Note that we use fact.times for >, otherwise
            # sorty_tuple is used, which also sorts by PK, which masks 2 facts
            # at same time but with unique IDs.
            # - This also shows that we update self.curr_index already, and
            #   maybe self.curr_group, but not self.curr_fact (so the state
            #   is outta sorts).
            self.controller.affirm(self.curr_fact.start >= prev_fact.end)
            # We (re)wired the fact to the group earlier; now rewire the group.
            self.fulfill_jump(prev_fact, reason='fact-dec')
            # See if we've identified the boundary of the known factiverse.
            if prev_fact.start <= self.beginning_of_time:
                with self.fact_group_rekeyed():
                    self.curr_group.claim_time_span(since=SinceTimeBegan)
                self.controller.affirm(self.curr_group.since_time_began)
            self.controller.client_logger.debug('\n- prev: {}'.format(prev_fact.short))
            return prev_fact

        # ***

        def fetch_prev_fact():
            # Check curr_fact.curr_index, and not curr_fact.has_prev_fact,
            # because the facts may not all be wired yet.
            if self.curr_index > 0:
                return from_curr_group_decrement()
            else:
                # Choose between fact from store or previous group (if any).
                return from_prev_group_or_store()

        # ***

        def from_curr_group_decrement():
            self.curr_index -= 1
            prev_from_curr_group = self.curr_group[self.curr_index]
            return prev_from_curr_group

        # ***

        def curr_group_add_prev(prev_fact):
            self.controller.affirm(self.curr_fact.prev_fact is None)
            self.curr_group_add(prev_fact)
            if self.curr_group[self.curr_index] is not prev_fact:
                # Added gap-fact, which comes after previous fact
                # we already decremented to reference.
                self.curr_index += 1
            self.controller.affirm(self.curr_group[self.curr_index] is prev_fact)
            return prev_fact

        # ***

        def from_prev_group_or_store():
            prev_from_store = self.fetch_prev_from_store()
            if overlaps_current_fact(prev_from_store):
                return fix_overlapping_fact(prev_from_store)
            if exists_in_between_groups(prev_from_store):
                # Add the fact to the group, but do not wire yet,
                # as we may add a gap fact, if necessary.
                return curr_group_add_prev(prev_from_store)
            # No facts between this group and previous group;
            # or there are no facts from store
            #  nor is there a previous group.
            return squash_group_prev()

        # ^^^

        def overlaps_current_fact(prev_from_store):
            if prev_from_store is None:
                return False
            return prev_from_store.end > self.curr_group.time_since

        def fix_overlapping_fact(prev_from_store):
            un_undoable_fact_prev = prev_from_store.copy()
            un_undoable_fact_prev.end = self.curr_group.time_since
            un_undoable_fact_prev.start = min(
                un_undoable_fact_prev.start,
                self.curr_group.time_since,
            )
            un_undoable_fact_prev.dirty_reasons.add('overlapped')
            # (lb): A hack to tell other UX components to alert user.
            un_undoable_fact_prev.dirty_reasons.add('alert-user')
            return curr_group_add_prev(un_undoable_fact_prev)

        # ^^^

        def exists_in_between_groups(prev_from_store):
            if prev_from_store is None:
                return False
            prev_group, prev_group_index = fetch_prev_group()
            if prev_group is None:
                return True
            if prev_from_store.start < prev_group.time_until:
                return False
            self.controller.affirm(prev_from_store.end <= self.curr_group.time_since)
            return True

        def fetch_prev_group():
            prev_group_index = self.groups.index(self.curr_group) - 1
            if prev_group_index >= 0:
                return self.groups[prev_group_index], prev_group_index
            return None, None

        # ^^^

        def squash_group_prev():
            self.controller.affirm(self.curr_index == 0)
            prev_group, prev_group_index = fetch_prev_group()
            if prev_group is None:
                return None
            return collapse_group(prev_group, prev_group_index)

        def collapse_group(prev_group, prev_group_index):
            prev_fact = prev_group[-1]
            with self.fact_group_rekeyed():
                _prev_group = self.groups.pop(prev_group_index)
                self.controller.affirm(prev_group is _prev_group)
                self.curr_index = len(prev_group) - 1
                # Note that addition returns a new object, e.g.,
                #  self.curr_group = prev_group + self.curr_group
                # sets self.curr_group to a new object -- but fact_group_rekeyed
                # adds back the original group object, so do in-place addition.
                # Note that slice operator calls __setitem__ for each fact,
                # whereas addition calls __add__ or __radd__ just once.
                self.curr_group[:] = prev_group + self.curr_group
            self.controller.affirm(self.curr_group[self.curr_index] is prev_fact)
            return prev_fact

        # ***

        def fill_gap_since(prev_fact):
            if (prev_fact is not None) and prev_fact.has_next_fact:
                self.controller.affirm(prev_fact.next_fact is self.curr_fact)
                return prev_fact
            self.controller.affirm(not self.curr_fact.has_prev_fact)
            if prev_fact is None:
                gap_or_prev = fill_gap_since_users_life_began()
            else:
                gap_or_prev = fill_gap_since_prev_fact(prev_fact)
            if gap_or_prev is None:
                return None
            if gap_or_prev is not prev_fact:
                curr_group_add_prev(gap_or_prev)
            wire_two_facts_since(gap_or_prev, prev_fact)
            return gap_or_prev

        def fill_gap_since_users_life_began():
            gap_fact = None
            user_start_time = self.beginning_of_time
            if self.curr_fact.start > user_start_time:
                gap_fact = self.fact_from_interval_gap(
                    user_start_time, self.curr_fact.start,
                )
            return gap_fact

        def fill_gap_since_prev_fact(prev_fact):
            if prev_fact.end == self.curr_fact.start:
                gap_fact = prev_fact
            elif prev_fact.is_gap:
                # Prior fact is already unedited interval gap, so just edit its time.
                prev_fact.end = self.curr_fact.start
                gap_fact = prev_fact
            else:
                gap_fact = self.fact_from_interval_gap(
                    prev_fact.end, self.curr_fact.start,
                )
            return gap_fact

        def wire_two_facts_since(gap_or_prev, prev_fact):
            if prev_fact is not None:
                if prev_fact is not gap_or_prev:
                    self.wire_two_facts_neighborly(prev_fact, gap_or_prev)
                else:
                    self.wire_two_facts_neighborly(gap_or_prev, self.curr_fact)
            self.controller.affirm(gap_or_prev.end == self.curr_fact.start)
            self.controller.affirm(gap_or_prev.next_fact is self.curr_fact)
            self.controller.affirm(self.curr_fact.prev_fact is gap_or_prev)
            return gap_or_prev

        return _jump_fact_dec()

    # ***

    def fetch_prev_from_store(self, ref_time=None):
        ref_time = ref_time or self.curr_group.time_since
        # Momentaneous Facts support.
        ref_fact = None
        if ref_time == self.curr_group[0].start:
            ref_fact = self.curr_group[0]
        # Search backward from the start time of the group (rather than,
        # say, calling antecedent(self.curr_fact)), so that we skip time
        # that's currently under our control.
        prev_from_store = self.controller.facts.antecedent(
            fact=ref_fact, ref_time=ref_time,
        )
        if not prev_from_store:
            # No more prior facts from store.
            return None
        # Prior fact should at least have a start time.
        self.controller.affirm(prev_from_store.start)
        # In case we decide to keep this fact, make it safe.
        prev_from_store.orig_fact = 0  # The orig_fact is... itself!
        # The caller will figure out if the previous fact from the
        # store is one that is not yet under our control; or if it's
        # one we already know about (in which case, there exists a
        # group already blocking that time window).
        return prev_from_store

