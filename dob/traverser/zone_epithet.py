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
"""Facts Carousel Header (Fact meta and diff)"""

from __future__ import absolute_import, unicode_literals

from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.widgets import Label

__all__ = [
    'ZoneEpithet',
]


class ZoneEpithet(object):
    """"""
    def __init__(self, carousel):
        self.carousel = carousel

    def standup(self):
        # FIXME/2019-01-21: Old comment: "Rename style key".
        #   Probably compile list of style names first
        #   and make sure they each fit a common theme.
        self.header_help_style = self.carousel.chosen_style['header-help_text']

    # ***

    def rebuild_viewable(self):
        """"""
        def _rebuild_viewable():
            self.facts_diff = self.carousel.zone_manager.facts_diff
            assemble_children()
            self.epithet_container = build_container()
            self.refresh_all_children()
            return self.epithet_container

        def assemble_children():
            self.children = []
            add_fact_banner()

        def add_fact_banner():
            add_interval_banner()

        # ***

        def add_interval_banner():
            self.interval_banner = Label(text='')
            self.children.append(self.interval_banner)

        # ***

        def build_container():
            epithet_container = HSplit(children=self.children)
            return epithet_container

        # ***

        return _rebuild_viewable()

    # ***

    def refresh_all_children(self):
        self.refresh_interval()

    # ***

    def selectively_refresh(self):
        self.refresh_interval()

    # ***

    def refresh_interval(self):
        tod_humanize = self.facts_diff.edit_fact.time_of_day_humanize
        interval_text = tod_humanize(show_now=True)
        self.interval_banner.text = self.bannerize(interval_text)

    # ***

    # Interval as currently formatted has max 53 chars, e.g.,
    MAX_INTERVAL_WIDTH = len('Mon 01 Jan 2120 ◐ 12:00 AM — 11:59 PM 31 Dec 2120')

    def bannerize(self, text):
        def _bannerize():
            bannerful = colorful_banner_town(text)
            parts = []
            parts += [('', '\n')]
            parts += [(self.header_help_style, bannerful)]
            parts += [('', '\n')]
            return parts

        def colorful_banner_town(text):
            # 53 ch max, e.g., Fri 13 Jul 2018 ◐ 11:40 PM — 12:29 AM Sat 14 Jul 2018
            padded_text = '{0:<{1}}'.format(text, 53)
            centered_text = '{0:^{1}}'.format(
                padded_text, self.carousel.avail_width - 1,
            )
            banner = '''
╭─────────────────────────────────────────────────────────────────────────────────────────╮
│{0}│
╰─────────────────────────────────────────────────────────────────────────────────────────╯
            '''.format(centered_text).lstrip("\n").rstrip()
            return banner

        return _bannerize()

