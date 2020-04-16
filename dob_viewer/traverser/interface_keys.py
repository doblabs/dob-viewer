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

import time

from gettext import gettext as _

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

from dob_bright.termio import dob_in_user_warning

from dob_prompt.prompters.interface_bonds import KeyBond

from ..config import json_load_sublisted

__all__ = (
    'KeyBonder',
)


# ***

class KeyBonder(object):

    def __init__(self, config):
        self.config = config
        self.errors = []
        self.keyed_factoids = {}

    # ***

    KEYBONDS_CFG_SECTION = 'editor-keys'

    def _key_bonds(
        self, action_map, action_name, config_name=None, config_section=None,
    ):
        """"""
        def __key_bonds():
            action, cfgval = resolve_action_cfgval()
            keybonds = build_bonds(action, cfgval)
            return keybonds

        def resolve_action_cfgval():
            editor_keys = config_section or KeyBonder.KEYBONDS_CFG_SECTION
            cfgname = config_name or action_name
            action = getattr(action_map, action_name)
            cfgval = self.config[editor_keys][cfgname]
            return action, cfgval

        def build_bonds(action, cfgval):
            # Note that the json loader discards any entry that would just
            # be the empty string (which the user can apply to a key binding to
            # effectively "disable" (render unreachable) the associated command).
            keycodes, errmsg = json_load_sublisted(action_name, cfgval)
            if errmsg is not None:
                return self.add_error_and_return_empty(errmsg)
            keybonds = [KeyBond(keycode, action=action) for keycode in keycodes]
            return keybonds

        return __key_bonds()

    def add_error_and_return_empty(self, errmsg):
        self.errors.append(errmsg)
        return []

    # ***

    def make_bindings(self, key_bonds):
        """"""
        def _make_bindings():
            key_bindings = KeyBindings()
            [add_binding(key_bindings, keyb) for keyb in key_bonds]
            return key_bindings

        def add_binding(key_bindings, keyb):
            try:
                add_binding_str_or_list(key_bindings, keyb)
            except Exception as err:
                self.errors.append(_(
                    'ERROR: Failed to add a key binding for ‘{}’: “{}”'
                    .format(keyb.action.__name__, str(err))
                ))

        def add_binding_str_or_list(key_bindings, keyb):
            # YOU: Toss an eager=True to the add if you think PTK is
            # hooking a binding. Or check your tmux config, mayhap.
            if isinstance(keyb.keycode, str):
                key_bindings.add(keyb.keycode)(keyb.action)
            else:
                key_bindings.add(*keyb.keycode)(keyb.action)

        return _make_bindings()

    # ***

    @property
    def date_separators(self):
        try:
            return self._date_separators
        except AttributeError:
            return self._load_date_separators()

    def _load_date_separators(self):
        editor_keys = KeyBonder.KEYBONDS_CFG_SECTION
        cfgname = 'date_separators'
        date_seps = self.config[editor_keys][cfgname]
        self._date_separators, errmsg = json_load_sublisted(cfgname, date_seps)
        if errmsg is not None:
            return self.add_error_and_return_empty(errmsg)
        return self._date_separators

    # ***

    def print_warnings(self):
        if not self.errors:
            return
        dob_in_user_warning('\n'.join(self.errors))
        time.sleep(2.666)
        self.errors = []

    # ***

    def widget_focus(self, action_map):
        key_bonds = []
        # Use the 'focus_next' config value as the key to wire
        # to the action_map.focus_next handler.
        key_bonds += self._key_bonds(action_map, 'focus_next')
        key_bonds += self._key_bonds(action_map, 'focus_previous')
        # Bindings to edit time are always available (and toggle focus when repeated).
        key_bonds += self._key_bonds(action_map, 'edit_time_start')
        key_bonds += self._key_bonds(action_map, 'edit_time_end')
        return key_bonds

    # ***

    def save_and_quit(self, action_map):
        key_bonds = []
        # Save Facts command is where you'd expect it.
        key_bonds += self._key_bonds(action_map, 'save_edited_and_live')
        key_bonds += self._key_bonds(action_map, 'save_edited_and_exit')
        # User can always real-quit, but prompted if edits.
        key_bonds += self._key_bonds(action_map, 'exit_command')
        # User can soft-cancel if they have not edited.
        key_bonds += self._key_bonds(action_map, 'exit_quietly')
        return key_bonds

    # ***

    def edit_time(self, action_map):
        key_bonds = []
        key_bonds += self._key_bonds(action_map, 'edit_time_enter')
        key_bonds += self._key_bonds(action_map, 'toggle_focus_description')
        # By default, PPT will add any key we don't capture to active widget's
        # buffer, but we'll override so we can ignore alpha characters.
        key_bonds += [KeyBond(Keys.Any, action=action_map.edit_time_any_key)]
        return key_bonds

    # ***

    def undo_redo(self, action_map, context):
        key_bonds = []
        key_bonds += self._key_bonds(
            action_map, 'undo_command_{}'.format(context), 'undo_command',
        )
        key_bonds += self._key_bonds(
            action_map, 'redo_command_{}'.format(context), 'redo_command',
        )
        return key_bonds

    # ***

    def normal(self, action_map):
        key_bonds = []

        key_bonds += self._key_bonds(action_map, 'rotate_help')
        key_bonds += self._key_bonds(action_map, 'dev_breakpoint')

        key_bonds += self._key_bonds(action_map, 'jump_fact_dec')
        key_bonds += self._key_bonds(action_map, 'jump_fact_inc')

        key_bonds += self._key_bonds(action_map, 'jump_day_dec')
        key_bonds += self._key_bonds(action_map, 'jump_day_inc')

        key_bonds += self._key_bonds(action_map, 'jump_rift_dec')
        key_bonds += self._key_bonds(action_map, 'jump_rift_inc')

        key_bonds += self._key_bonds(action_map, 'jump_fact_first')
        key_bonds += self._key_bonds(action_map, 'jump_fact_final')

        key_bonds += self._key_bonds(action_map, 'cursor_up_one')
        key_bonds += self._key_bonds(action_map, 'cursor_down_one')

        key_bonds += self._key_bonds(action_map, 'scroll_up')
        key_bonds += self._key_bonds(action_map, 'scroll_down')
        key_bonds += self._key_bonds(action_map, 'scroll_top')
        key_bonds += self._key_bonds(action_map, 'scroll_bottom')

        # FIXME/BACKLOG: Search feature. E.g., like Vim's /:
        #   KeyBond('/', action=zone_lowdown.start_search),
        # FIXME/BACKLOG: Filter feature.
        #   (By tag; matching text; dates; days of the week; etc.)

        # (lb): Not every Vim key needs to be mapped, e.g.,
        #  KeyBond('M', action=action_map.jump_fact_midpoint),
        # seems capricious, i.e., why implement if not just because we can?

        return key_bonds

    # ***

    def edit_fact(self, action_map):
        key_bonds = []
        key_bonds += self._key_bonds(action_map, 'edit_fact')
        key_bonds += self._key_bonds(action_map, 'edit_actegory')
        key_bonds += self._key_bonds(action_map, 'edit_description')
        key_bonds += self._key_bonds(action_map, 'edit_tags')
        return key_bonds

    # ***

    def nudge_time(self, action_map):
        key_bonds = []
        key_bonds += self._key_bonds(action_map, 'edit_time_decrement_start')
        key_bonds += self._key_bonds(action_map, 'edit_time_increment_start')
        key_bonds += self._key_bonds(action_map, 'edit_time_decrement_end')
        key_bonds += self._key_bonds(action_map, 'edit_time_increment_end')
        key_bonds += self._key_bonds(action_map, 'edit_time_decrement_both')
        key_bonds += self._key_bonds(action_map, 'edit_time_increment_both')
        key_bonds += self._key_bonds(action_map, 'edit_time_decrement_start_5min')
        key_bonds += self._key_bonds(action_map, 'edit_time_increment_start_5min')
        key_bonds += self._key_bonds(action_map, 'edit_time_decrement_end_5min')
        key_bonds += self._key_bonds(action_map, 'edit_time_increment_end_5min')
        return key_bonds

    # ***

    def command_modifier(self, action_map):
        key_bonds = []
        key_bonds += self._key_bonds(action_map, 'allow_time_gap')
        key_bonds += [KeyBond(Keys.Any, action=action_map.command_modifier_any_key)]
        key_bonds += [KeyBond('c-h', action=action_map.backspace_command_modifier)]
        return key_bonds

    # ***

    def create_delete_fact(self, action_map):
        return []  # FIXME/2020-04-11: Implement or get off the pot!

        # FIXME/2020-04-11: Not implemented:
        key_bonds = []
        key_bonds += self._key_bonds(action_map, 'fact_split')
        key_bonds += self._key_bonds(action_map, 'fact_erase')
        key_bonds += self._key_bonds(action_map, 'fact_merge_prev')
        key_bonds += self._key_bonds(action_map, 'fact_merge_next')
        return key_bonds

    # ***

    def clipboard(self, action_map):
        key_bonds = []
        key_bonds += self._key_bonds(action_map, 'fact_copy_fact')
        key_bonds += self._key_bonds(action_map, 'fact_cut')
        key_bonds += self._key_bonds(action_map, 'fact_paste')
        key_bonds += self._key_bonds(action_map, 'fact_copy_activity')
        key_bonds += self._key_bonds(action_map, 'fact_copy_tags')
        key_bonds += self._key_bonds(action_map, 'fact_copy_description')
        return key_bonds

    # ***

    def shortcuts(self, action_map):
        key_bonds = []
        key_bonds += self._key_bonds(action_map, 'copy_complete_and_paste_active')
        key_bonds += self._key_bonds(action_map, 'copy_complete_and_paste_new')
        key_bonds += self._key_bonds(action_map, 'complete_and_prompt_new')
        return key_bonds

    # ***

    FACTOID_CFG_SECTION = 'custom-paste'
    FACTOID_CFG_MAPPING = 'mapping_'
    FACTOID_CFG_FACTOID = 'factoid_'

    def custom_factoids(self, action_map):
        self.keyed_factoids = {}
        key_bonds = []
        config_idx = 0
        custom_paste = KeyBonder.FACTOID_CFG_SECTION
        while True:
            config_idx += 1
            mapping_name = '{}{}'.format(KeyBonder.FACTOID_CFG_MAPPING, config_idx)
            try:
                custom_bonds = self._key_bonds(
                    action_map,
                    'custom_factoid_paste',
                    config_name=mapping_name,
                    config_section=custom_paste,
                )
            except AttributeError:
                # No more custom mappings!
                break
            if custom_bonds:
                custom_bond = custom_bonds[0]
                factoid_name = '{}{}'.format(KeyBonder.FACTOID_CFG_FACTOID, config_idx)
                try:
                    custom_factoid = self.config[custom_paste][factoid_name]
                except AttributeError:
                    self.errors.append(_(
                        'ERROR: Custom key mapping ‘{}’ has not matching factoid: “{}”'
                        .format(mapping_name, factoid_name)
                    ))
                else:
                    self.keyed_factoids[custom_bond.keycode] = custom_factoid
                    key_bonds += [custom_bond]
        return key_bonds

    # ***

    def begin_commando(self, action_map):
        # The Colon Commando! Because (by default) type ':' then command + 'ENTER'.
        # I.e., a Vim-like command mode.
        key_bonds = []
        key_bonds += self._key_bonds(action_map, 'begin_commando')
        return key_bonds

    def going_commando(self, action_map):
        key_bonds = []
        # So Ctrl-c is not user configurable. Go configure.
        key_bonds += [KeyBond('c-c', action=action_map.cancel_commando)]
        key_bonds += [KeyBond(Keys.Any, action=action_map.parts_commando)]
        key_bonds += [KeyBond('c-h', action=action_map.backspace_commando)]
        key_bonds += self._key_bonds(action_map, 'final_commando')
        return key_bonds

    # ***

    def begin_delta_time(self, action_map):
        key_bonds = []
        key_bonds += self._key_bonds(action_map, 'begin_delta_time_start')
        key_bonds += self._key_bonds(action_map, 'begin_delta_time_end')
        return key_bonds

    def going_delta_time(self, action_map):
        key_bonds = []
        # Any non-recognizable key cancels the binding, or Ctrl-C, which is
        # otherwise not handled unless we explicitly do so.
        key_bonds += [KeyBond('c-c', action=action_map.cancel_delta_time)]
        key_bonds += [KeyBond(Keys.Any, action=action_map.parts_delta_time)]
        key_bonds += [KeyBond('c-h', action=action_map.backspace_delta_time)]
        key_bonds += self._key_bonds(action_map, 'allow_time_gap')
        key_bonds += self._key_bonds(action_map, 'final_delta_time_apply')
        key_bonds += self._key_bonds(action_map, 'final_delta_time_minutes')
        key_bonds += self._key_bonds(action_map, 'final_delta_time_hours')
        return key_bonds

