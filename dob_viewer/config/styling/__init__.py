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

"""User configurable interactive editor styling settings loaders."""

from gettext import gettext as _

from dob_bright.termio import dob_in_user_warning

from .. import pause_on_error_message_maybe

__all__ = (
    'load_obj_from_internal',
)


def load_obj_from_internal(
    controller,
    obj_name,
    internal,
    default_name=None,
    warn_tell_not_found=False,
    config_key='',
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
        msg = _('Nothing matches “{0}”, from config setting “{1}”, in “{2}”.').format(
            obj_name, config_key, internal.__name__,
        )
        controller.client_logger.warning(msg)
        dob_in_user_warning(msg)  # Also blather to stdout.
        # If `dob edit`, linger, otherwise user unlikely to see the message.
        pause_on_error_message_maybe(controller.ctx)

    def debug_loaded_default(loaded_obj):
        controller.affirm(loaded_obj is not None)  # Because you specified default!
        controller.client_logger.debug(
            _('Loaded default object for “{0}”.'.format(obj_name))
        )

    return _load_obj_from_internal()

