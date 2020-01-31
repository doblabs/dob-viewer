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

"""GroupChained, an ordered Facts list."""

from gettext import gettext as _

from nark.items.fact import SinceTimeBegan, UntilTimeStops
from sortedcontainers import SortedKeyList

__all__ = (
    'GroupChained',
    'sorted_facts_list',
)


# ***

def integer_range_groupify(integers):
    from itertools import groupby
    from operator import itemgetter

    def _integer_range_groupify():
        srtd = sorted(map(int, integers))
        return assemble_groups(srtd)

    def range_key_recursive(srtd, ix):
        if ix[0] == 0:
            # Very first item, so always start of group.
            return ix[1]
        prev_idx = ix[0] - 1
        prev_val = int(srtd[prev_idx])
        if ix[1] == prev_val + 1:
            # Previous item value is 1 before this one, so walk backwards.
            return range_key_recursive(srtd, (prev_idx, prev_val,))
        return ix[1]

    def range_key(srtd, ix):
        key = range_key_recursive(srtd, ix)
        # print('ix:', ix, 'key:', key)
        return key

    def assemble_groups(srtd):
        grouped = []
        for key, grp in groupby(enumerate(srtd), lambda ix: range_key(srtd, ix)):
            # print('key: {} / grp: {} {}'.format(key, grp, list(grp)))
            # print(list(map(itemgetter(1), grp)))
            grouped.append(list(map(itemgetter(1), grp)))
        return grouped

    return _integer_range_groupify()


# ***

def sorted_facts_list(facts=None):
    sorted_facts_list = SortedKeyList(
        iterable=facts,
        # Use sorty_times, not sorty_tuple, to ignore PKs. Otherwise, two facts
        # with the same PK would not appear as equivalent, which would make the
        # fact-finding insertion/update/removal code less easily maintainable.
        key=lambda item: item.sorty_times,
    )
    return sorted_facts_list


# ***

class GroupChained(object):
    """
    A GroupChained represents an ordered list of Facts.
    In the context of the Carousel, the ordered list
    is also guaranteed to be contiguous, and may contain
    a mix of stored Facts, new Facts, and gap Facts.
    Or even no Facts, if group is simply claiming time.
    """
    # FIXME/2019-12-06: (lb): Just testing. Remove affirm arg. later.
    # def __init__(self, facts=None):
    def __init__(self, facts=None, affirm=None):
        self.facts = sorted_facts_list(facts)
        self.reset_time_window()
        self.affirm = affirm or (lambda _x: None)

    # ***

    def __add__(self, other):
        return GroupChained(facts=self.facts + other.facts)

    def __radd__(self, other):
        return GroupChained(facts=other.facts + self.facts)

    # ***

    def __delitem__(self, key):
        del self.facts[key]

    def __getitem__(self, key):
        return self.facts[key]

    # For, e.g., self.group[:] = ...
    def __setitem__(self, key, value):
        del self.facts[key]
        try:
            # For, e.g., self.group[:] = ...
            # value is a slice().
            for fact in value.facts:
                self.facts.add(fact)
            self.claim_fact_time(value.facts)
        except AttributeError:
            # For, e.g., self.group[0] = ...
            # value is a (Placeable)Fact.
            self.facts.add(value)

    # ***

    def __iter__(self):
        return iter(self.facts)

    def __len__(self):
        return len(self.facts)

    # ***

    def __eq__(self, other):
        if self is other:
            return True
        if (other is not None) and isinstance(other, GroupChained):
            other = other.times
        return self.times == other

    def __gt__(self, other):
        return self.times > other.times

    def __lt__(self, other):
        return self.times < other.times

    # ***

    def __str__(self):
        def range_str(grp):
            if len(grp) == 0:
                return 'No IDs!'
            elif len(grp) == 1:
                return '{}'.format(grp[0])
            else:
                lhs = grp[0]
                rhs = grp[-1]
                if grp[1] < 0:
                    lhs, rhs = rhs, lhs
                return '{} to {}'.format(lhs, rhs)

        def assemble_pk_ranges():
            # 2019-12-03: (lb): Cull Fact(s) with pk == None.
            # - I fixed a bug: I added a tag, and saved. But self.facts here
            # had a fact with pk == None, to wit: str(None) returned 'None',
            # and integer_range_groupify blew up on ValueError.
            # - I'd like to confidently note why facts.pk is None, so affirming.
            facts = list(filter(None, self.facts))
            # FIXME/2019-12-06: (lb): Just testing. Remove affirm later.
            self.affirm(len(facts) == len(self.facts))
            pks = [str(fact.pk) for fact in facts]
            grouped = integer_range_groupify(pks)
            pk_ranges = ', '.join([range_str(grp) for grp in grouped])
            return len(pks), pk_ranges

        num_pks, pk_ranges = assemble_pk_ranges()
        return _(
            "‘{0}’ to ‘{1}’ / No. Facts: {2} / PK(s): {3}"
        ).format(self.time_since, self.time_until, num_pks, pk_ranges)

    # ***

    def claim_fact_time(self, facts=None):
        """NOTE: This function changes the SortedKeyList key, beware!"""
        if facts is None:
            facts = self.facts
        if not facts:
            return
        until = facts[-1].end or UntilTimeStops
        self.claim_time_span(since=facts[0].start, until=until)

    def claim_time_span(self, since=None, until=None):
        """NOTE: This function changes the SortedKeyList key, beware!"""
        # Handle since time.
        if self.time_since is None:
            self.time_since = since
        elif since is not None:
            self.time_since = min(self.time_since, since)
        # Handle until time.
        if self.time_until is None:
            self.time_until = until
        elif until is not None:
            self.time_until = max(self.time_until, until)

    def contains_fact_time(self, facts=None):
        if facts is None:
            facts = self.facts
        if not facts:
            return
        if (
            (facts[0].start < self.time_since)
            or (
                (facts[-1].end is None)
                and (self.time_until < UntilTimeStops)
            )
            or (
                (facts[-1].end is not None)
                and (facts[-1].end > self.time_until)
            )
        ):
            return False
        return True

    @property
    def sorty_times(self):
        return (self.time_since, self.time_until, )

    def reset_time_window(self):
        # Default to time window not defined (as opposed to empty
        # (impossible) time window achieved with (UntilTimeStops,
        # SinceTimeBegan)).
        self.time_since = None
        self.time_until = None
        self.claim_fact_time()

    @property
    def since_time_began(self):
        return self.time_since is SinceTimeBegan

    @property
    def until_time_stops(self):
        return self.time_until is UntilTimeStops

    # ***

    def add(self, some_fact):
        # Caller Beware: This changes the group key!
        self.facts.add(some_fact)
        self.claim_fact_time([some_fact])

    def bisect_key_left(self, key):
        return self.facts.bisect_key_left(key)

    def bisect_left(self, value):
        return self.facts.bisect_left(value)

    def index(self, some_fact):
        for index, fact in enumerate(self.facts):
            if some_fact.pk == fact.pk:
                return index
        raise ValueError("Fact with PK '{0}' is not in list".format(some_fact.pk))

    def pop(self, index):
        return self.facts.pop(index)

