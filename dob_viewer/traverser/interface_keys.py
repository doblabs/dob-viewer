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

"""Key Binding Wiring Manager"""

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

from dob_prompt.prompters.interface_bonds import KeyBond

__all__ = (
    'KeyBonder',
    'make_bindings',
)


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

class KeyBonder(object):

    def __init__(self, config):
        self.config = config

    # ***

    def _key_bond(self, action_map, action_name, config_name=None):
        if config_name is None:
            config_name = action_name
        action = getattr(action_map, action_name)
        keycode = self.config['editor-keys'][config_name]
        return KeyBond(keycode, action=action)

    # ***

    def widget_focus(self, action_map):
        key_bonds_widget_focus = [
            # Use the 'focus_next' config value as the key to wire
            # to the action_map.focus_next handler.
            self._key_bond(action_map, 'focus_next'),
            self._key_bond(action_map, 'focus_previous'),
            # Bindings to edit time are always available (and toggle focus when repeated).
            self._key_bond(action_map, 'edit_time_start'),
            self._key_bond(action_map, 'edit_time_end'),
        ]
        return key_bonds_widget_focus

    # ***

    def save_and_quit(self, action_map):
        key_bonds_save_and_quit = [
            # Save Facts command is where you'd expect it.
            self._key_bond(action_map, 'save_edited_and_live'),
            self._key_bond(action_map, 'save_edited_and_exit'),
            # User can soft-cancel if they have not edited.
            self._key_bond(action_map, 'cancel_softly'),
            # User can always real-quit, but prompted if edits.
            self._key_bond(action_map, 'cancel_command'),
            # NOTE: Using 'escape' to exit is slow because PPT waits to
            #       see if escape sequence follows (which it wouldn't, after
            #       an 'escape', but meta-combinations start with an escape).
            #   tl;dr: 'escape' to exit slow b/c alias resolution.
            # Note that 'escape' here is the actual ESCape key,
            # and not to be confused with the meta key character,
            # e.g., using ('escape', 'm') to capture Alt-m (m-m).
            KeyBond('escape', action=action_map.cancel_softly),
        ]
        return key_bonds_save_and_quit

    # ***

    def edit_time(self, zone_details):
        handler = zone_details
        key_bonds_edit_time = [
            KeyBond('enter', action=handler.editable_text_enter),
            KeyBond('d', action=handler.toggle_focus_description),
            # By default, PPT will add any key we don't capture to active widget's
            # buffer, but we'll override so we can ignore alpha characters.
            KeyBond(Keys.Any, action=handler.editable_text_any_key),
        ]
        return key_bonds_edit_time

    # ***

    def undo_redo(self, action_map_or_zone_details):
        handler = action_map_or_zone_details
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

    def normal(self, action_map):
        key_bonds_normal = [
            KeyBond('?', action=action_map.rotate_help),
            #
            # 2020-03-30: (lb): Was using PPT-HOTH fork and had m- mappings, e.g.,
            #   KeyBond('m-=', action=action_map.dev_breakpoint),
            KeyBond((Keys.Escape, '='), action=action_map.dev_breakpoint),
            #
            KeyBond('j', action=action_map.jump_fact_dec),
            KeyBond('k', action=action_map.jump_fact_inc),
            KeyBond(Keys.Left, action=action_map.jump_fact_dec),
            KeyBond(Keys.Right, action=action_map.jump_fact_inc),
            #
            KeyBond('J', action=action_map.jump_day_dec),
            KeyBond('K', action=action_map.jump_day_inc),
            # These are only wired to Escape then Arrow, not Meta-Arrow...
            KeyBond((Keys.Escape, Keys.Left), action=action_map.jump_day_dec),
            KeyBond((Keys.Escape, Keys.Right), action=action_map.jump_day_inc),
            #
            KeyBond(('g', 'g'), action=action_map.jump_rift_dec),
            KeyBond('G', action=action_map.jump_rift_inc),
            # (lb): Not every Vim key needs to be mapped, e.g.,
            #  KeyBond('M', action=action_map.jump_fact_midpoint),
            # seems capricious, i.e., why implement if not just because we can?
            #
            KeyBond('h', action=action_map.cursor_up_one),
            KeyBond('l', action=action_map.cursor_down_one),
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
                action=action_map.ignore_key_press_noop,
            ),
            KeyBond(  # Alt-DOWN
                ('escape', '[', '1', ';', '4', 'B'),
                action=action_map.ignore_key_press_noop,
            ),
            KeyBond(  # Alt-RIGHT [bunch of snowflakes]
                ('escape', '[', '1', ';', '4', 'C'),
                action=action_map.ignore_key_press_noop,
            ),
            KeyBond(  # Alt-LEFT
                ('escape', '[', '1', ';', '4', 'D'),
                action=action_map.ignore_key_press_noop,
            ),
            #
            KeyBond('pageup', action=action_map.scroll_up),
            KeyBond('pagedown', action=action_map.scroll_down),
            KeyBond('home', action=action_map.scroll_top),
            KeyBond('end', action=action_map.scroll_bottom),
            #
            # FIXME/BACKLOG: Search feature. E.g., like Vim's /:
            #   KeyBond('/', action=zone_lowdown.start_search),
            # FIXME/BACKLOG: Filter feature.
            #   (By tag; matching text; dates; days of the week; etc.)
        ]
        return key_bonds_normal

    # ***

    def edit_fact(self, action_map):
        key_bonds_edit_fact = [
            # Raw Fact Editing. With a Capital E.
            KeyBond('E', action=action_map.edit_fact),
            # Edit act@gory, description, and tags using prompt__awesome.
            # (lb): This is pretty cool. prompt_awesome was built first,
            # and then I got comfortable with PPT and built the Carousel,
            # and then I was able to stick one inside the other, and it's
            # just awesome awesome now.
            KeyBond('a', action=action_map.edit_actegory),
            KeyBond('d', action=action_map.edit_description),
            KeyBond('t', action=action_map.edit_tags),
        ]
        return key_bonds_edit_fact

    # ***

    def nudge_time_with_arrows(self, action_map):
        key_bonds_nudge_time_with_arrows = [
            KeyBond('s-left', action=action_map.edit_time_decrement_start),
            KeyBond('s-right', action=action_map.edit_time_increment_start),
            KeyBond('c-left', action=action_map.edit_time_decrement_end),
            KeyBond('c-right', action=action_map.edit_time_increment_end),
            # FIXME/2019-01-21: Can you check if running in Terminator
            #  and warn-tell user. And/Or: Customize Key Binding feature.
            # In Terminator: Shift+Ctrl+Left/+Right: Resize the terminal left/right.
            #  (lb): I've disabled the 2 bindings in Terminator,
            #   so this works for me... so fixing it is a low priority!
            KeyBond('s-c-left', action=action_map.edit_time_decrement_both),
            KeyBond('s-c-right', action=action_map.edit_time_increment_both),
        ]
        return key_bonds_nudge_time_with_arrows

    # ***

    def create_delete_fact(self, action_map):
        key_bonds_create_delete_fact = [
            # 2020-03-30: (lb): Was using PPT-HOTH fork and had m- mappings, e.g.,
            #   KeyBond('m-p', action=action_map.fact_split),
            #   KeyBond('m-e', action=action_map.fact_erase),
            #   KeyBond(('m-m', Keys.Left), action=action_map.fact_merge_prev),
            #   KeyBond(('m-m', Keys.Right), action=action_map.fact_merge_next),
            KeyBond((Keys.Escape, 'p'), action=action_map.fact_split),
            KeyBond((Keys.Escape, 'e'), action=action_map.fact_erase),
            KeyBond((Keys.Escape, 'm', Keys.Left), action=action_map.fact_merge_prev),
            KeyBond((Keys.Escape, 'm', Keys.Right), action=action_map.fact_merge_next),
        ]
        return key_bonds_create_delete_fact

    # ***

    def clipboard(self, action_map):
        key_bonds_clipboard = [
            #
            KeyBond('c-c', action=action_map.fact_copy_fact),
            KeyBond('c-x', action=action_map.fact_cut),
            KeyBond('c-v', action=action_map.fact_paste),
            #
            KeyBond(('A', 'c-c'), action=action_map.fact_copy_activity),
            KeyBond(('T', 'c-c'), action=action_map.fact_copy_tags),
            KeyBond(('D', 'c-c'), action=action_map.fact_copy_description),
        ]
        return key_bonds_clipboard

