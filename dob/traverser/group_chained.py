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
"""Facts Carousel"""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

from sortedcontainers import SortedKeyList

__all__ = [
    'GroupChained',
    'sorted_facts_list',
]


def sorted_facts_list(facts=None):
    sorted_facts_list = SortedKeyList(
        iterable=facts,
        key=lambda item: item.sorty_tuple,
    )
    return sorted_facts_list


class GroupChained(object):
    def __init__(self, facts=None):
        self.facts = sorted_facts_list(facts)

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
        except AttributeError:
            # For, e.g., self.group[0] = ...
            # value is a (Placeable)Fact.
            self.facts.add(value)

    def __len__(self):
        return len(self.facts)

    def __str__(self):
        pks = [str(fact.pk) for fact in self.facts]
        return _(
            "‘{0}’ to ‘{1}’ / No. Facts: {2} / PK(s): {3}"
        ).format(self.first_time, self.final_time, len(pks), ', '.join(pks))

    def __eq__(self, other):
        if self is other:
            return True
        if (other is not None) and isinstance(other, GroupChained):
            other = other.sorty_tuple
        return self.sorty_tuple == other

    def __gt__(self, other):
        # Not called...
        return self.sorty_tuple > other.sorty_tuple

    def __lt__(self, other):
        # Not called...
        return self.sorty_tuple < other.sorty_tuple

    def __add__(self, other):
        return GroupChained(facts=self.facts + other.facts)

    def __radd__(self, other):
        return GroupChained(facts=other.facts + self.facts)

    @property
    def sorty_tuple(self):
        if len(self.facts) == 0:
            return None
        return self.facts[0].sorty_tuple

    @property
    def first_time(self):
        if len(self.facts) == 0:
            return None
        return self.facts[0].start

    @property
    def final_time(self):
        if len(self.facts) == 0:
            return None
        return self.facts[-1].end

    def add(self, some_fact):
        self.facts.add(some_fact)

    def bisect_key_left(self, key):
        return self.facts.bisect_key_left(key)

    def bisect_left(self, value):
        return self.facts.bisect_left(value)

    def index(self, some_fact):
        for index, fact in enumerate(self.facts):
            if some_fact.pk == fact.pk:
                return index
        return ValueError("Fact with PK '{0}' is not in list".format(some_fact.pk))

