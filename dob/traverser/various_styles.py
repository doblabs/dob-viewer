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
""""""

from __future__ import absolute_import, unicode_literals

__all__ = [
    'color',
    'light',
    'night',
]


def default():
    """Default defines all options so tweaked stylings may omit any."""
    styling = {}
    styling['container-syles'] = [
        ('content-area', 'bg:#000000 #FFFFFF'),
        ('content-help', 'bg:#000000 #FFFFFF'),
        ('interval-gap', 'bg:#000000 #FFFFFF'),
        ('unsaved-fact', 'bg:#000000 #FFFFFF'),
        ('category-sleep', 'bg:#000000 #FFFFFF'),
    ]
    styling['header-help_text'] = 'bg:#000000 #FFFFFF bold'
    styling['root-app_align'] = 'LEFT'
    styling['content-height'] = 10
    styling['content-width'] = 90
    styling['content-wrap'] = True
    return styling


def color():
    styling = default()
    styling['container-syles'] = [
        # Loosely based on such and such color palette:
        #
        #   http://paletton.com/#uid=3000u0kg0qB6pHIb0vBljljq+fD

        # Default Fact.description frame background.
        # ('content-area', 'bg:#00aa00 #000000'),
        # ('content-area', 'bg:#D0EB9A #000000'),
        ('content-area', 'bg:#9BC2C2 #000000'),

        # Fact.description background when showing help.
        # ('content-help', 'bg:#0000aa #000000'),
        # ('content-help', 'bg:#226666 #000000'),
        ('content-help', 'bg:#66AAAA #000000'),

        # Other contextual Fact.description background colors.

        # FIXME: BACKLOG: Interval Gappage.
        # ('interval-gap', 'bg:#cc0000 #000000'),
        # ('interval-gap', 'bg:#FCA5A5 #000000'),
        ('interval-gap', 'bg:#AA6C39 #000000'),

        # FIXME: BACKLOG: Highlight edited Facts (yet to be saved).
        # ('unsaved-fact', 'bg:#0000cc #000000'),
        # ('unsaved-fact', 'bg:#639797 #000000'),
        ('unsaved-fact', 'bg:#D0EB9A #000000'),

        ('category-sleep', 'bg:#CA85AC #000000'),

        ('header-focus', 'bg:#00FFFF #0000FF'),
    ]
    styling['header-help_text'] = 'fg:#5F5FFF bold'
    styling['root-app_align'] = 'JUSTIFY'
    return styling


def light():
    styling = default()
    styling['container-syles'] = [
        ('content-area', 'bg:#FFFFFF #000000'),
        ('content-help', 'bg:#FFFFFF #000000'),
        ('interval-gap', 'bg:#FFFFFF #000000'),
        ('unsaved-fact', 'bg:#FFFFFF #000000'),
        ('category-sleep', 'bg:#FFFFFF #000000'),
    ]
    styling['header-help_text'] = 'bg:#FFFFFF #000000 bold'
    styling['root-app_align'] = 'LEFT'
    return styling


def night():
    styling = default()
    styling['container-syles'] = [
        ('content-area', 'bg:#000000 #FFFFFF'),
        ('content-help', 'bg:#000000 #FFFFFF'),
        ('interval-gap', 'bg:#000000 #FFFFFF'),
        ('unsaved-fact', 'bg:#000000 #FFFFFF'),
        ('category-sleep', 'bg:#000000 #FFFFFF'),
    ]
    styling['header-help_text'] = 'bg:#000000 #FFFFFF bold'
    styling['root-app_align'] = 'LEFT'
    return styling

