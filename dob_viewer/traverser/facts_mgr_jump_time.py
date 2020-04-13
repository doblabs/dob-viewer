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

"""Facts Carousel"""

from datetime import timedelta

__all__ = (
    'FactsManager_JumpTime',
)


class FactsManager_JumpTime(object):
    """"""
    def __init__(self, *args, **kwargs):
        super(FactsManager_JumpTime, self).__init__()

        self._jump_time_reference = None

    # ***

    @property
    def jump_time_reference(self):
        self.debug('get: {}'.format(
            self._jump_time_reference or '{} (reset)'.format(self.curr_fact.start)
        ))
        if not self._jump_time_reference:
            if not self.curr_fact.end:
                # If user is looking at Active Fact, and they want to, e.g.,
                # see Fact 1 day ago, use now time, not start of Fact, or
                # we might show a Fact before one they'd naturally expect.
                time_ref = self.controller.now
            else:
                # (lb): For any other Fact, I dunno, split the diff.
                half_delta = (self.curr_fact.end - self.curr_fact.start) / 2
                time_ref = self.curr_fact.start + half_delta
            self.jump_time_reference = time_ref
        return self._jump_time_reference

    @jump_time_reference.setter
    def jump_time_reference(self, jump_time_reference):
        self.debug('set: {}'.format(jump_time_reference))
        self._jump_time_reference = jump_time_reference

    # ***

    def jump_day_dec(self, days=1):
        prev_day = self.jump_time_reference - timedelta(days=days)
        prev_fact = self.jump_to_fact_nearest(until_time=prev_day)
        if prev_fact is None:
            prev_fact = self.jump_to_oldest_fact(reason='day-dec')
        return prev_fact

    def jump_day_inc(self, days=1):
        next_day = self.jump_time_reference + timedelta(days=days)
        next_fact = self.jump_to_fact_nearest(since_time=next_day)
        if next_fact is None:
            next_fact = self.jump_to_latest_fact(reason='day-inc')
        return next_fact

