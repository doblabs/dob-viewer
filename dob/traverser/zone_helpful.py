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

__all__ = (
    'CAROUSEL_HELP',
)


# FIXME: Make a crude help. Maybe later make it splashier (different colors, etc.).
#        NOTE: Current multi-line widget does not take inline styling;
#                show what's the proper way to style things?
#              OR: Should we build the Help with widgets for each binding?
CAROUSEL_HELP = _(
    """ ┏━━━━━━━━━ NAVIGATION ━━━━━━━━━┳━━━━ EDITING ━━━━┳━━━━━━━ INTERVAL ━━━━━━━━┓
 ┃ → / ←    Next/Previous Fact  ┃  [e] Edit Fact  ┃   Add/Subtract 1 min.   ┃
 ┃ j / k      Same as → / ←     ┠─────────────────╂─────────────────────────┨
 ┃ ↑ / ↓    Move Cursor Up/Down ┃    Or edit:     ┃  To Start: Shift → / ←  ┃
 ┃ h / l      Same as ↑ / ↓     ┃  [a]  act@gory  ┃  To End:    Ctrl → / ←  ┃
 ┃ PgUp     Move Cursor Up/Down ┃  [t]  tagslist  ┃  To Both:               ┃
 ┃  PgDn      by pageful        ┃  [d]  descript  ┃       Ctrl-Shift → / ←  ┃
 ┣━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━┻━━━━━┳━━━━━━━━━━━┻━━━━━━━━━┳━━━━━━━━━━━━━━━┫
 ┃  [?] Read   ┃   Ctrl-S  ┃  Ctrl-Q  ┃  [c-p] Split Fact ½ ┃   [u]   Undo  ┃
 ┃  More Help  ┃    Save   ┃   Exit   ┃  [c-e] Empty Fact   ┃  [c-r]  Redo  ┃
 ┣━━━━━━━━━━━━━┻━━━━━━━━━━━┻━━━━┳━━━━━┻━━━━━━━━━━━┳━━━━━━━━━┻━━━━━━━━━━━━━━━┫
 ┃ [g-g]    Jump to First Fact  ┃ H A M S T E R   ┃    H A M S T E R        ┃
 ┃  [G]     Jump to Final Fact  ┃  H A M S T E R  ┃     H A M S T E R       ┃
 ┠──────────────────────────────╂─────────────────╂─────────────────────────┨
 ┃ [Home]   First line Descript ┃  H A M S T E R  ┃      H A M S T E R      ┃
 ┃ [End]    Bottom of Descript. ┃   H A M S T E R ┃       H A M S T E R     ┃
 ┣━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━┻━━━━━┯━━━━━━━━━┯━┻━━━━━━━┳━━━━━━━━━━━━━━━━━┫
 ┃  [?] Close  ┃  [q] Easy  ┃  [c-c]  │  [c-x]  │  [c-v]  ┃   [c-z]  Undo   ┃
 ┃  this Help  ┃    Exit    ┃   Copy  │   Cut   │  Paste  ┃   [c-y]  Redo   ┃
 ┗━━━━━━━━━━━━━┻━━━━━━━━━━━━┻━━━━━━━━━┷━━━━━━━━━┷━━━━━━━━━┻━━━━━━━━━━━━━━━━━┛

    """.rstrip()
)


NUM_HELP_PAGES = 2

