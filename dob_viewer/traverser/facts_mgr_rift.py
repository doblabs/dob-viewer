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

__all__ = (
    'FactsManager_Rift',
)


class FactsManager_Rift(object):
    """"""
    def __init__(self, *args, **kwargs):
        super(FactsManager_Rift, self).__init__()

        self.time_rifts = []

    # ***

    def place_time_rifts(self):
        def _place_time_rifts():
            self.time_rifts = []
            for group in self.groups:
                first_fact = self.find_first_dirty_from_group(group)
                if first_fact is None:
                    first_fact = group[0]
                add_time_rift(first_fact)
            last_group_last_fact = self.groups[-1][-1]
            if self.time_rifts[-1] != last_group_last_fact.start:
                add_time_rift(last_group_last_fact)

        def add_time_rift(some_fact):
            self.controller.client_logger.debug(
                'time_rifts: {}'.format(some_fact.start),
            )
            self.time_rifts.append(some_fact.start)

        _place_time_rifts()

    def find_rift_fact(self, is_next=False, is_prev=False):
        def _find_rift_fact():
            assert is_next ^ is_prev
            prev_time, next_time = drop_time_bounds()
            since_time = next_time if is_next else None
            until_time = prev_time if is_prev else None
            if not since_time and not until_time:
                return None
            rift_fact = self.jump_to_fact_nearest(
                since_time=since_time,
                until_time=until_time,
            )
            return rift_fact

        def drop_time_bounds():
            prev_start = None
            for start_time in self.time_rifts:
                if self.curr_fact.start < start_time:
                    return (prev_start, start_time)
                if start_time != self.curr_fact.start:
                    prev_start = start_time
            return (prev_start, None)

        return _find_rift_fact()

    def find_first_dirty(self):
        for group in self.groups:
            first_dirty_fact = self.find_first_dirty_from_group(group)
            if first_dirty_fact is not None:
                return first_dirty_fact
        # None edited/dirty. Fall back on last fact (most recent).
        return self.groups[-1][-1]

    def find_first_dirty_from_group(self, group):
        for fact in group:
            if fact.dirty:
                return fact
        return None

