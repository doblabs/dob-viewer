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

"""Key Binding Action Manager"""

from prompt_toolkit.application.application import _CombinedRegistry
from prompt_toolkit.key_binding.key_processor import KeyProcessor

from .interface_keys import (
    KeyBonder,
)
from .key_action_map import KeyActionMap

__all__ = (
    'ActionManager',
)


class ActionManager(object):
    """"""
    def __init__(self, carousel):
        self.carousel = carousel

    # ***

    def standup(self):
        self.key_action_map = KeyActionMap(self.carousel)
        self.key_bonder = KeyBonder(
            config=self.carousel.controller.config,
        )
        self.setup_key_bindings()

    def finalize_standup(self):
        self.key_bonder.print_warnings()

    # ***

    def _wire_keys(self, key_bindings):
        application = self.carousel.zone_manager.application
        previous_bindings = application.key_bindings
        application.key_bindings = key_bindings
        # A thing of beauty. What a hack job. (lb): I added this to support the
        # commando feature, but it may have always been missing (but I did not
        # notice because I wasn't throwing key combos at the time widgets); or
        # it might be that PTK 3.0 changes now demand it. Rebuild the key_processor,
        # otherwise the key_bindings just wired have no effect.
        application.key_processor = KeyProcessor(_CombinedRegistry(application))
        return previous_bindings

    def wire_keys_command_mode(self, key_bindings):
        # Set focus to something without an input control. Otherwise, if we leave
        # focus on time widget, the _CombinedRegistry will add keybindings for it!
        self.previous_control = self.carousel.zone_manager.layout.current_control
        self.carousel.zone_manager.layout.focus(
            self.carousel.zone_manager.zone_content.content
        )
        # SOOOOOO hacky. Love it! Disable cursor (otherwise there's a white
        # rectangle at 0,0 in the content window.)
        current_window = self.carousel.zone_manager.layout.current_window
        self.previous_hide_cursor = current_window.always_hide_cursor
        current_window.always_hide_cursor = lambda: True
        # Finally, wire the commando key bindings and handlers.
        self.previous_bindings = self._wire_keys(key_bindings)

    def unwire_keys_command_mode(self):
        # Enable content window to show cursor next time it's focused.
        current_window = self.carousel.zone_manager.layout.current_window
        current_window.always_hide_cursor = self.previous_hide_cursor
        self.previous_hide_cursor = None
        # Re-focus whatever widget was active before commando mode.
        self.carousel.zone_manager.layout.focus(self.previous_control)
        self.previous_control = None
        # Re-wire keys wired before commando mode.
        self._wire_keys(self.previous_bindings)
        self.previous_bindings = None

    # ***

    def wire_keys_normal(self):
        self._wire_keys(self.key_bindings_normal)

    def wire_keys_edit_time(self):
        self._wire_keys(self.key_bindings_edit_time)

    def wire_keys_modal(self):
        self._wire_keys(self.key_bindings_modal)

    def wire_keys_commando(self):
        self.wire_keys_command_mode(self.key_bindings_commando)

    def unwire_keys_commando(self):
        self.unwire_keys_command_mode()

    def wire_keys_delta_time(self):
        self.wire_keys_command_mode(self.key_bindings_delta_time)

    def unwire_keys_delta_time(self):
        self.unwire_keys_command_mode()

    # ***

    def setup_key_bindings(self):
        self.setup_key_bindings_shared()
        self.setup_key_bindings_normal()
        self.setup_key_bindings_edit_time()
        self.setup_key_bindings_modal()
        self.setup_key_bindings_commando()
        self.setup_key_bindings_delta_time()

    def setup_key_bindings_shared(self):
        bindings = []
        bindings += self.key_bonder.save_and_quit(self.key_action_map)
        bindings += self.key_bonder.widget_focus(self.key_action_map)
        bindings += self.key_bonder.begin_commando(self.key_action_map)

        self.key_bindings_shared = bindings

    def setup_key_bindings_normal(self):
        bindings = []
        bindings += self.key_bonder.normal(self.key_action_map)
        bindings += self.key_bonder.edit_fact(self.key_action_map)
        bindings += self.key_bonder.nudge_time(self.key_action_map)
        bindings += self.key_bonder.begin_delta_time(self.key_action_map)
        bindings += self.key_bonder.command_modifier(self.key_action_map)
        bindings += self.key_bonder.create_delete_fact(self.key_action_map)
        bindings += self.key_bonder.clipboard(self.key_action_map)
        bindings += self.key_bonder.undo_redo(self.key_action_map, 'content')
        bindings += self.key_bonder.shortcuts(self.key_action_map)
        bindings += self.key_bonder.custom_factoids(self.key_action_map)
        bindings += self.key_bindings_shared

        self.key_bindings_normal = self.key_bonder.make_bindings(bindings)

    def setup_key_bindings_edit_time(self):
        bindings = []
        bindings += self.key_bonder.edit_time(self.key_action_map)
        bindings += self.key_bonder.undo_redo(self.key_action_map, 'edit_time')
        bindings += self.key_bindings_shared

        self.key_bindings_edit_time = self.key_bonder.make_bindings(bindings)

    def setup_key_bindings_modal(self):
        bindings = []
        # None. Modal has its own for the basics.
        # SKIP: bindings += self.key_bindings_shared
        self.key_bindings_modal = self.key_bonder.make_bindings(bindings)

    def setup_key_bindings_commando(self):
        bindings = []
        bindings += self.key_bonder.going_commando(self.key_action_map)
        # SKIP: bindings += self.key_bindings_shared
        self.key_bindings_commando = self.key_bonder.make_bindings(bindings)

    def setup_key_bindings_delta_time(self):
        bindings = []
        bindings += self.key_bonder.going_delta_time(self.key_action_map)
        # SKIP: bindings += self.key_bindings_shared
        self.key_bindings_delta_time = self.key_bonder.make_bindings(bindings)

