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
"""Key Binding Action Manager"""

from __future__ import absolute_import, unicode_literals

from .interface_keys import (
    key_bonds_edit_time,
    key_bonds_global,
    key_bonds_shared,
    key_bonds_update,
    key_bonds_undo_redo,
    make_bindings
)
from .key_action_map import KeyActionMap


__all__ = [
    'ActionManager',
]


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

    # ***

    def setup_key_bindings(self):
        self.setup_key_bindings_shared()
        self.setup_key_bindings_normal()
        self.setup_key_bindings_edit_time()

    def setup_key_bindings_shared(self):
        self.key_bindings_shared = key_bonds_shared(self.key_action_map)

    def setup_key_bindings_normal(self):
        bindings = []
        bindings += key_bonds_global(self.key_action_map)
        bindings += key_bonds_update(self.carousel.update_handler)
        bindings += key_bonds_undo_redo(self.carousel.update_handler)
        bindings += self.key_bindings_shared

        self.key_bindings_normal = make_bindings(bindings)

    def setup_key_bindings_edit_time(self):
        bindings = []
        bindings += key_bonds_edit_time(self.carousel.zone_manager.zone_details)
        bindings += key_bonds_undo_redo(self.carousel.zone_manager.zone_details)
        bindings += self.key_bindings_shared

        self.key_bindings_edit_time = make_bindings(bindings)

