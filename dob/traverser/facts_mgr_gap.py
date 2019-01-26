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

from .placeable_fact import PlaceableFact

__all__ = [
    'FactsManager_Gap',
]


class FactsManager_Gap(object):
    """"""

    def fact_from_interval_gap(self, since_time, until_time):
        self.controller.affirm((not until_time) or (since_time < until_time))
        self.last_fact_pk -= 1
        gap_fact = PlaceableFact(
            pk=self.last_fact_pk,
            activity=None,
            start=since_time,
            end=until_time,
        )
        gap_fact.dirty_reasons.add('interval-gap')
        # Mark deleted until edited, so gap is not saved unless edited.
        gap_fact.deleted = True
        gap_fact.orig_fact = 0  # self-referential
        return gap_fact

    def wire_two_facts_neighborly(self, fact_1, fact_2):
        self.controller.affirm(fact_1 < fact_2)
        self.controller.affirm(fact_2.prev_fact is None)
        self.controller.affirm(fact_1.next_fact is None)
        fact_1.next_fact = fact_2
        fact_2.prev_fact = fact_1

