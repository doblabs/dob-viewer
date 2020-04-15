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

"""FactsManager_FactInc"""

from nark.items.fact import UntilTimeStops

__all__ = (
    'FactsManager_FactInc',
)


# SYNC_ME: Keep FactsManager_FactDec and FactsManager_FactInc synced.
#   That, or write a generic base class, but that sounds painfuller to maintain.
#   then simply running meld as necessary:
#
#       meld facts_mgr_fact_dec.py facts_mgr_fact_inc.py &
class FactsManager_FactInc(object):
    """"""
    def jump_fact_inc(self):
        """"""
        def _jump_fact_inc():
            # Check first if we've reached the ending of all time.
            is_final_fact = (self.curr_index == (len(self.curr_group) - 1))
            if (
                is_final_fact
                and not self.curr_fact.end
                and self.curr_group.until_time_stops
            ):
                return None
            # Each facts group represents a contiguous block of time that is
            # being managed by dob, and to ignore anything in the store from
            # that time. Find either the next fact under dob's control,
            # or one from the store (that we'll wire into dob in a later step).
            next_fact = fetch_next_fact()
            # Each fact's next_fact and prev_fact links are not wired until
            # we inspect them here for gaps -- meaning, we fill in the gap facts
            # reactively, as the user traverses the facts in the carousel. Now.
            next_fact = fill_gap_until(next_fact)
            # If we've reached the ending of all time, there's nothing following.
            if next_fact is None:
                return None
            # Just a sanity check. Note that we use fact.times for >, otherwise
            # sorty_tuple is used, which also sorts by PK, which masks 2 facts
            # at same time but with unique IDs.
            # - This also shows that we update self.curr_index already, and
            #   maybe self.curr_group, but not self.curr_fact (so the state
            #   is outta sorts).
            self.controller.affirm(self.curr_fact.end <= next_fact.start)
            # We (re)wired the fact to the group earlier; now rewire the group.
            self.fulfill_jump(next_fact, reason='fact-inc')
            # See if we've identified the boundary of the known factiverse.
            if (next_fact.end is None) or (next_fact.end is UntilTimeStops):
                self.controller.affirm(self.curr_group.until_time_stops)
            self.controller.client_logger.debug('\n- next: {}'.format(next_fact.short))
            return next_fact

        # ***

        def fetch_next_fact():
            # Check curr_fact.curr_index, and not curr_fact.has_next_fact,
            # because the facts may not all be wired yet.
            self.curr_index < (len(self.curr_group) - 1)
            if self.curr_index < (len(self.curr_group) - 1):
                return from_curr_group_increment()
            else:
                # Choose between fact from store or next group (if any).
                return from_next_group_or_store()

        # ***

        def from_curr_group_increment():
            self.curr_index += 1
            next_from_curr_group = self.curr_group[self.curr_index]
            return next_from_curr_group

        # ***

        def curr_group_add_next(next_fact):
            self.controller.affirm(self.curr_fact.next_fact is None)
            self.curr_group_add(next_fact)
            if self.curr_group[self.curr_index] is not next_fact:
                self.curr_index += 1
            self.controller.affirm(self.curr_group[self.curr_index] is next_fact)
            return next_fact

        # ***

        def from_next_group_or_store():
            next_from_store = self.fetch_next_from_store()
            if overlaps_current_fact(next_from_store):
                return fix_overlapping_fact(next_from_store)
            if exists_in_between_groups(next_from_store):
                # Add the fact to the group, but do not wire yet,
                # as we may add a gap fact, if necessary.
                return curr_group_add_next(next_from_store)
            # No facts between this group and next group;
            # or there are no facts from store
            #  nor is there a next group.
            return squash_group_next()

        # ^^^

        def overlaps_current_fact(next_from_store):
            if next_from_store is None:
                return False
            return next_from_store.start < self.curr_group.time_until

        def fix_overlapping_fact(next_from_store):
            un_undoable_fact_next = next_from_store.copy()
            un_undoable_fact_next.start = self.curr_group.time_until
            un_undoable_fact_next.end = max(
                un_undoable_fact_next.end,
                self.curr_group.time_until,
            )
            un_undoable_fact_next.dirty_reasons.add('overlapped')
            # (lb): A hack to tell other UX components to alert user.
            un_undoable_fact_next.dirty_reasons.add('alert-user')
            return curr_group_add_next(un_undoable_fact_next)

        # ^^^

        def exists_in_between_groups(next_from_store):
            if next_from_store is None:
                return False
            next_group, next_group_index = fetch_next_group()
            if next_group is None:
                return True
            next_from_store_end = next_from_store.end or UntilTimeStops
            if next_from_store_end > next_group.time_since:
                return False
            self.controller.affirm(next_from_store.start >= self.curr_group.time_until)
            return True

        def fetch_next_group():
            next_group_index = self.groups.index(self.curr_group) + 1
            if next_group_index < len(self.groups):
                return self.groups[next_group_index], next_group_index
            return None, None

        # ^^^

        def squash_group_next():
            self.controller.affirm(self.curr_index == (len(self.curr_group) - 1))
            next_group, next_group_index = fetch_next_group()
            if next_group is None:
                return None
            return collapse_group(next_group, next_group_index)

        def collapse_group(next_group, next_group_index):
            next_fact = next_group[0]
            with self.fact_group_rekeyed():
                # The rekeyed fcn., pops curr_group, so decrement next index.
                next_group_index -= 1
                _next_group = self.groups.pop(next_group_index)
                self.controller.affirm(next_group is _next_group)
                self.curr_index += 1
                # Note that addition returns a new object, e.g.,
                #  self.curr_group += next_group
                # sets self.curr_group to a new object -- but fact_group_rekeyed
                # adds back the original group object, so do in-place addition.
                # Note that slice operator calls __setitem__ for each fact,
                # whereas addition calls __add__ or __radd__ just once.
                self.curr_group[:] = self.curr_group + next_group
            self.controller.affirm(self.curr_group[self.curr_index] is next_fact)
            return next_fact

        # ***

        def fill_gap_until(next_fact):
            if (next_fact is not None) and next_fact.has_prev_fact:
                self.controller.affirm(next_fact.prev_fact is self.curr_fact)
                return next_fact
            self.controller.affirm(not self.curr_fact.has_next_fact)
            if next_fact is None:
                gap_or_next = fill_gap_is_endless()
            else:
                gap_or_next = fill_gap_until_fact(next_fact)
            if gap_or_next is None:
                self.controller.affirm(False)  # 2020-04-15: (lb): Impossible?
                return None
            if gap_or_next is not next_fact:
                curr_group_add_next(gap_or_next)
            wire_two_facts_until(gap_or_next, next_fact)
            return gap_or_next

        def fill_gap_is_endless():
            gap_fact = self.fact_from_interval_gap(
                self.curr_fact.end, None,
            )
            return gap_fact

        def fill_gap_until_fact(next_fact):
            if next_fact.start == self.curr_fact.end:
                gap_fact = next_fact
            elif next_fact.is_gap:
                # Next fact is already unedited interval gap, so just edit its time.
                next_fact.start = self.curr_fact.end
                gap_fact = next_fact
            else:
                gap_fact = self.fact_from_interval_gap(
                    self.curr_fact.end, next_fact.start,
                )
            return gap_fact

        def wire_two_facts_until(gap_or_next, next_fact):
            if next_fact is not None:
                if next_fact is not gap_or_next:
                    self.wire_two_facts_neighborly(gap_or_next, next_fact)
                else:
                    self.wire_two_facts_neighborly(self.curr_fact, gap_or_next)
            self.controller.affirm(self.curr_fact.end == gap_or_next.start)
            self.controller.affirm(gap_or_next.prev_fact is self.curr_fact)
            self.controller.affirm(self.curr_fact.next_fact is gap_or_next)
            return gap_or_next

        return _jump_fact_inc()

    # ***

    def fetch_next_from_store(self, ref_time=None):
        ref_time = ref_time or self.curr_group.time_until
        # To process momentaneous Facts properly (and, e.g., to avoid finding
        # the same empty-time Fact again and again), send the Fact to the data
        # store lookup method, so that it can use the PK in the query.
        ref_fact = None
        if ref_time == self.curr_group[-1].end:
            ref_fact = self.curr_group[-1]
        # Search forward from the end time of the group (rather than,
        # say, calling subsequent(self.curr_fact)), so that we skip time
        # that's currently under our control.
        next_from_store = self.controller.facts.subsequent(
            fact=ref_fact, ref_time=ref_time,
        )
        if not next_from_store:
            # No more later facts from store.
            return None
        # Next fact should at least have a start time.
        self.controller.affirm(next_from_store.start)
        # In case we decide to keep this fact, make it safe.
        next_from_store.orig_fact = 0  # The orig_fact is... itself!
        # The caller will figure out if the next fact from the
        # store is one that is not yet under our control; or if it's
        # one we already know about (in which case, there exists a
        # group already blocking that time window).
        return next_from_store

