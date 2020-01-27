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

from .interface_keys import (
    key_bonds_clipboard,
    key_bonds_edit_time,
    key_bonds_normal,
    key_bonds_save_and_quit,
    key_bonds_undo_redo,
    key_bonds_update,
    key_bonds_widget_focus,
    make_bindings
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
        self.setup_key_bindings()

    # ***

    def wire_keys_normal(self):
        application = self.carousel.zone_manager.application
        application.key_bindings = self.key_bindings_normal

    def wire_keys_edit_time(self):
        application = self.carousel.zone_manager.application
        application.key_bindings = self.key_bindings_edit_time

    def wire_keys_modal(self):
        application = self.carousel.zone_manager.application
        application.key_bindings = self.key_bindings_modal

    # ***

    def setup_key_bindings(self):
        self.setup_key_bindings_shared()
        self.setup_key_bindings_normal()
        self.setup_key_bindings_edit_time()
        self.setup_key_bindings_modal()

    def setup_key_bindings_shared(self):
        bindings = []
        bindings += key_bonds_save_and_quit(self.key_action_map)
        bindings += key_bonds_widget_focus(self.key_action_map)

        self.key_bindings_shared = bindings

    def setup_key_bindings_normal(self):
        bindings = []
        bindings += key_bonds_normal(self.key_action_map)
        bindings += key_bonds_update(self.key_action_map)
        bindings += key_bonds_clipboard(self.key_action_map)
        bindings += key_bonds_undo_redo(self.key_action_map)
        bindings += self.key_bindings_shared

        self.key_bindings_normal = make_bindings(bindings)

    def setup_key_bindings_edit_time(self):
        bindings = []
        bindings += key_bonds_edit_time(self.carousel.zone_manager.zone_details)
        bindings += key_bonds_undo_redo(self.carousel.zone_manager.zone_details)
        bindings += self.key_bindings_shared

        self.key_bindings_edit_time = make_bindings(bindings)

    def setup_key_bindings_modal(self):
        bindings = []

        self.key_bindings_modal = make_bindings(bindings)

