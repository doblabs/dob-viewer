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
"""Fact Editing State Machine"""

from __future__ import absolute_import, unicode_literals

from collections import namedtuple

from nark.items import Fact

__all__ = [
    'PlaceableFact',
]


FactoidSource = namedtuple(
    'FactoidSource', ('line_num', 'line_raw'),
)


class PlaceableFact(Fact):
    """"""
    def __init__(
        self,
        *args,
        dirty_reasons=None,
        line_num=None,
        line_raw=None,
        **kwargs
    ):
        super(PlaceableFact, self).__init__(*args, **kwargs)
        # For tracking edits between store saves.
        self.dirty_reasons = dirty_reasons or set()
        # For identifying errors in the input.
        self.parsed_source = FactoidSource(line_num, line_raw)
        self.orig_fact = None
        self.next_fact = None
        self.prev_fact = None

    def copy(self, *args, **kwargs):
        """
        """
        new_fact = super(PlaceableFact, self).copy(*args, **kwargs)
        new_fact.dirty_reasons = set(list(self.dirty_reasons))
        new_fact.parsed_source = self.parsed_source
        new_fact.orig_fact = self.orig_fact
        # SKIP: next_fact, prev_fact.
        return new_fact

    @classmethod
    def create_from_factoid(cls, factoid, *args, **kwargs):
        """
        """
        new_fact, err = super(PlaceableFact, cls).create_from_factoid(
            factoid, *args, **kwargs
        )
        if new_fact is not None:
            line_num = 1
            line_raw = factoid
            new_fact.parsed_source = FactoidSource(line_num, line_raw)
        return new_fact, err

    @property
    def dirty(self):
        return self.unstored or len(self.dirty_reasons) > 0

    def reset_orig(self):
        if self.orig is None:
            return
        self = self.orig

    @property
    def unstored(self):
        return (not self.pk) or (self.pk < 0)

