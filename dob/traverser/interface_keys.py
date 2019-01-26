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
"""Key Binding Wiring Manager"""

from __future__ import absolute_import, unicode_literals

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

from ..prompters.interface_bonds import KeyBond

__all__ = [
    'key_bonds_edit_time',
    'key_bonds_global',
    'key_bonds_shared',
    'key_bonds_update',
    'key_bonds_undo_redo',
    'make_bindings',
]


# ***

def make_bindings(key_bonds):
    key_bindings = KeyBindings()

    for keyb in key_bonds:
        if isinstance(keyb.keycode, tuple):
            key_bindings.add(*keyb.keycode)(keyb.action)
        else:
            key_bindings.add(keyb.keycode)(keyb.action)

    return key_bindings


# ***

def key_bonds_shared(handler):
    key_bonds_shared = [
        KeyBond('tab', action=handler.focus_next),
        KeyBond('s-tab', action=handler.focus_previous),
        KeyBond('c-q', action=handler.cancel_command),
    ]
    return key_bonds_shared


# ***

def key_bonds_edit_time(handler):
    key_bonds_edit_time = [
        KeyBond('enter', action=handler.editable_text_enter),
        # By default, PPT will add any key we don't capture to active widget's
        # buffer, but we'll override so we can ignore alphabetics [letters].
        KeyBond(Keys.Any, action=handler.editable_text_any_key),
        # FIXME/BACKLOG/2019-01-21: Ctrl-q should work while editing time.
        #  - And from any other state: editing act@gory, editing tags, anything else?
    ]
    return key_bonds_edit_time


# ***

def key_bonds_undo_redo(handler):
    key_bonds_undo_redo = [
        # Vim maps Ctrl-z and Ctrl-y for undo and redo;
        # and u/U to undo count/all and Ctrl-R to redo (count).
        KeyBond('c-z', action=handler.undo_command),
        KeyBond('c-y', action=handler.redo_command),
        # (lb): Too many options!
        # MAYBE: Really mimic all of Vi's undo/redo mappings,
        #        or just pick one each and call it good?
        KeyBond('u', action=handler.undo_command),
        KeyBond('c-r', action=handler.redo_command),
        # (lb): Oh so many duplicate redundant options!
        KeyBond('r', action=handler.redo_command),
    ]
    return key_bonds_undo_redo


# ***

def key_bonds_global(handler):
    key_bonds_global = [
        KeyBond('?', action=handler.rotate_help),
        #
        KeyBond('j', action=handler.scroll_left),
        KeyBond('k', action=handler.scroll_right),
        KeyBond(Keys.Left, action=handler.scroll_left),
        KeyBond(Keys.Right, action=handler.scroll_right),
        #
        # NOTE: It's not, say, 'm-left', but Escape-Arrow.
        # Ahahahaha, alt-arrows are special to Terminator, durp!
        KeyBond((Keys.Escape, Keys.Left), action=handler.scroll_left_day),
        KeyBond((Keys.Escape, Keys.Right), action=handler.scroll_right_day),
        KeyBond('J', action=handler.scroll_left_day),
        KeyBond('K', action=handler.scroll_right_day),
        #
        KeyBond('G', action=handler.scroll_fact_last),
        KeyBond(('g', 'g'), action=handler.scroll_fact_first),
        # MAYBE:
        #  KeyBond('M', action=handler.scroll_fact_middle),
        #
        KeyBond('h', action=handler.cursor_up_one),
        KeyBond('l', action=handler.cursor_down_one),
        #
        KeyBond('c-s', action=handler.finish_command),
        KeyBond('q', action=handler.cancel_softly),
        # NOTE: Using 'escape' to exit is slow because PPT waits to
        #       see if escape sequence follows (which it wouldn't, after
        #       an 'escape', but meta-combinations start with an escape).
        KeyBond('escape', action=handler.cancel_softly),
        #
        # FIXME: Oh, maybe make complicated handlers rather than hacking PPT lib?
        # NOTE: If you want to see how key presses map to KeyPresses, try:
        #         $ cd path/to/python-prompt-toolkit/tools
        #         $ python3 debug_vt100_input.py
        #         # PRESS ANY KEY
        # Catch Alt-Up explicitly -- though we don't do anything with it -- so
        # that the 'escape'-looking prefix does not trigger bare 'escape' handler.
        # ((lb): There might be a different way to do this... not sure.)
        KeyBond(  # Alt-UP
            ('escape', '[', '1', ';', '4', 'A'),
            action=handler.ignore_key_press_noop,
        ),
        KeyBond(  # Alt-DOWN
            ('escape', '[', '1', ';', '4', 'B'),
            action=handler.ignore_key_press_noop,
        ),
        KeyBond(  # Alt-RIGHT [bunch of snowflakes]
            ('escape', '[', '1', ';', '4', 'C'),
            action=handler.ignore_key_press_noop,
        ),
        KeyBond(  # Alt-LEFT
            ('escape', '[', '1', ';', '4', 'D'),
            action=handler.ignore_key_press_noop,
        ),
        #
        KeyBond('pageup', action=handler.scroll_up),
        KeyBond('pagedown', action=handler.scroll_down),
        KeyBond('home', action=handler.scroll_top),
        KeyBond('end', action=handler.scroll_bottom),
        #
        KeyBond('s', action=handler.edit_time_start),
        KeyBond('e', action=handler.edit_time_end),
    ]
    return key_bonds_global


# ***

def key_bonds_update(handler):
    key_bonds_update = [
        #
        KeyBond('E', action=handler.edit_fact),
        KeyBond('a', action=handler.edit_actegory),
        KeyBond('d', action=handler.edit_description),
        KeyBond('t', action=handler.edit_tags),
        #
        KeyBond('s-left', action=handler.edit_time_decrement_start),
        KeyBond('s-right', action=handler.edit_time_increment_start),
        KeyBond('c-left', action=handler.edit_time_decrement_end),
        KeyBond('c-right', action=handler.edit_time_increment_end),
        # Terminator: Shift+Ctrl+Left/+Right: Resize the terminal left/right.
        KeyBond('c-s-left', action=handler.edit_time_decrement_both),
        KeyBond('c-s-right', action=handler.edit_time_increment_both),
        #
        # (lb): 2018-06-28: Remaining are WIP. And I'm undecided on
        #       bindings. Maybe Alt-key bindings for Split & Clear?
        #       I like c-w and c-e because they're adjacent keys.
        #       Or m-w and m-e could also work, and then Ctrl-W is
        #       not confused with typical "close" command (whatever
        #       that would mean in Carousel context).
        # FIXME/2018-06-28: (lb): I'll clean this up. Eventually.
        #
        # KeyBond('c-p', action=handler.fact_split),
        # KeyBond('c-w', action=handler.fact_split),
        # KeyBond('c-t', action=handler.fact_split),
        #
        # KeyBond('c-e', action=handler.fact_wipe),
        # KeyBond('m-w', action=handler.fact_wipe),
        # KeyBond('c-a', action=handler.fact_wipe),
        KeyBond('m-p', action=handler.fact_split),
        KeyBond('m-e', action=handler.fact_wipe),
        #
        KeyBond('c-c', action=handler.fact_copy_fact),
        KeyBond('c-x', action=handler.fact_cut),
        KeyBond('c-v', action=handler.fact_paste),
        #
        # MAYBE/2018-07-19 09:07: Are these still useful bindings?
        # KeyBond(('F', 'c-c'), action=handler.fact_copy_all),
        KeyBond(('A', 'c-c'), action=handler.fact_copy_activity),
        KeyBond(('T', 'c-c'), action=handler.fact_copy_tags),
        KeyBond(('D', 'c-c'), action=handler.fact_copy_description),
    ]
    return key_bonds_update

