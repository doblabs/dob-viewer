# This file exists within 'dob-viewer':
#
#   https://github.com/tallybark/dob-viewer
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

from gettext import gettext as _

__all__ = (
    'render_carousel_help',
    'NUM_HELP_PAGES',
)


def render_carousel_help():
    # (lb): Is this sacrilegious, importing from that which installed *us*?
    # - I'll at least move the import inside the method. Then if this library
    #   is used outside dob (h. unlikely), the blowup will be localised.
    from dob import get_version as get_version_dob

    # FIXME/2020-04-01: Revisit this. Some commands changed; some were never implemented!
    carousel_help = _(
        """ ┏━━━━━━━━━ NAVIGATION ━━━━━━━━┳━━━━ PROMPTS ━━━━┳━━━━━━━ NUDGE TIME ━━━━━━━┓
 ┃ → / ←   Next/Previous Fact  ┃ a  edit act@cat ┃ [  Sub 1 min. from end   ┃
 ┃ j / k     Same as → / ←     ┃ t  edit tags    ┃ ]  Add 1 minute to end   ┃
 ┃ ↑ / ↓   Move Cursor Up/Down ┣━━━━ $EDITOR ━━━━┫ ,  Sub 1 min. from start ┃
 ┃ h / l     Same as ↑ / ↓     ┃ d  edit descrip.┃ .  Add 1 minute to start ┃
 ┃ PgUp    Move Cursor Up/Down ┣━━━━ COPIERS ━━━━┫ {{  Sub 5 mins from end   ┃
 ┃  PgDn     by pageful        ┃  c-c   a@c+tags ┃ }}  Add 5 mins to end     ┃
 ┃ Home    Top of Description  ┃  c-v    paste   ┃ <  Sub 5 mins from start ┃
 ┃  End      Bottom of Desc.   ┃ A c-c  copy a@c ┃ >  Add 5 mins to start   ┃
 ┣━━━ JUMP JUMP JUMP AROUND ━━━┫ T c-c  cpy tags ┃ Ctrl-Shift →  Nudge both ┃
 ┃ J / K   Back 1 day / Fwd. 1 ┃ D c-c  cpy desc ┃ Ctrl-Shift ←  Nudge both ┃
 ┃ [n]J/K  Back/Fwd [n] days   ┣━━━━━━━━━ RELATIVE TIME ADJUSTMENTS ━━━━━━━━┫
 ┃ f       Jump to First Fact  ┃ +[n]m  Set end [n] mins. after start time  ┃
 ┃ F       Jump to Final Fact  ┃ +[n]h  Set end [n] hours after start time  ┃
 ┃ YYYYMMDD f  Jump to date    ┃ -[n]m  Set start [n] mins. before end time ┃
 ┣━━━━━━━┳━━━━━━━┳━━━━━━┳━━━━━━┫ -[n]h  Set start [n] hours before end time ┃
 ┃ c-s   ┃ c-q   ┃ c-z  ┃ c-y  ┃ [n][ [n]]  Sub/Add [n] minutes from/to end ┃
 ┃ Save  ┃ Exit  ┃ Undo ┃ Redo ┃ [n], [n].  Sub/Add [n] mins. from/to start ┃
 ┣━━━━━━━┻━━━━━━━┻━━━━━━┻━━━━━━┻━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
 ┃ c-e  Copy curr. Fact meta onto Active Fact ┃ o  Complete Fact and prompt ┃
 ┃ V    Use curr. Fact meta to start new Fact ┃      for new Fact act@cat   ┃
 ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
 ┃     Learn more tricks at       ┃  Copyright © 2018-2020 Landon Bouma     ┃
 ┃   https://dob.readthedocs.io   ┃  dob v.{dob_vers: <32} ┃
 ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """
    ).format(
        dob_vers=get_version_dob()[:34],
    ).rstrip()
    return carousel_help


NUM_HELP_PAGES = 2

