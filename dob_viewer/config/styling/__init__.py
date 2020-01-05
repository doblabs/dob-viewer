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

"""User configurable interactive editor styling settings loaders."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

from ...helpers import dob_in_user_warning

__all__ = (
    'load_obj_from_internal',
)


def load_obj_from_internal(
    controller,
    obj_name,
    internal,
    default_name=None,
    warn_tell_not_found=False,
):
    """"""

    def _load_obj_from_internal():
        loaded_obj = try_loading_internal(internal, obj_name)
        if loaded_obj is None:
            warn_tell_on_object_not_found(obj_name)
            if default_name:
                loaded_obj = try_loading_internal(internal, default_name)
                debug_loaded_default(loaded_obj)
        return loaded_obj

    def try_loading_internal(internal, obj_name):
        if not obj_name:
            return None
        # See if this is one of the basic baked-in styles/lexers/things.
        return getattr(internal, obj_name, None)

    def warn_tell_on_object_not_found(obj_name):
        if not obj_name or not warn_tell_not_found:
            return
        msg = _('No object from “{0}” named “{1}”.').format(
            internal.__name__, obj_name,
        )
        controller.client_logger.warning(msg)
        dob_in_user_warning(msg)  # Also blather to stdout.

    def debug_loaded_default(loaded_obj):
        controller.affirm(loaded_obj is not None)  # Because you specified default!
        controller.client_logger.debug(
            _('Loaded default object for “{0}”.'.format(obj_name))
        )

    return _load_obj_from_internal()

