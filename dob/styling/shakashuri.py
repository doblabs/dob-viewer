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

from __future__ import absolute_import, unicode_literals

from prompt_toolkit.styles import Style


def carousel_style():
    style = Style([

        # FIXME/2018-07-10 08:52: Harmupf. I want --no-color to work,
        #   but implementing that may require knowing how the
        #   customization of colors will work.
        #   ... you may need an chjson parser!

        # A palette:
        #  http://paletton.com/#uid=3000u0kg0qB6pHIb0vBljljq+fD

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

        # FIXME: BACKLOG: User-selectable category highlights.
        # ('category-sleep', 'bg:#009900 #000000'),
        ('category-sleep', 'bg:#CA85AC #000000'),
    ])
    return style

