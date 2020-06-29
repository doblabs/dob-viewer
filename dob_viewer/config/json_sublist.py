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

"""dob_viewer.config sub.package provides Carousel UX user configuration settings."""

import json

from gettext import gettext as _

__all__ = (
    'json_load_sublisted',
)


def json_load_sublisted(cfgname, cfgval):
    def _json_load_sublisted():
        # (lb): We could skip the startswith check and just use except,
        #       but it feels more readable this way.
        if not cfgval.startswith('['):
            # Just a string. Except don't bother with the empty string,
            # which is used to disable a key command mapping.
            if cfgval:
                return [cfgval], None
            return [], None
        try:
            # List of lists: Top-level is list, and elements are lists.
            # - This is currently used for keybindings, which can either
            #   be a single element sublist (representing a single key),
            #   or the sublist could be a key binding tuple (well, it's
            #   json, so a list), which represents a multiple-key binding.
            keycodes = json.loads(cfgval)
            assert isinstance(keycodes, list)  # Would it be anything else?
            if not sanity_check(keycodes):
                return None, error_not_list_within_lists()
        except json.decoder.JSONDecodeError as err:
            return None, error_not_list_within_lists(err)
        return keycodes, None

    def sanity_check(keycodes):
        return all(isinstance(keycode, list) for keycode in keycodes)

    def error_not_list_within_lists(err=''):
        append_err = ' (“{}”)'.format(err) if err else ''
        return (_(
            'ERROR: Key binding for ‘{}’ should be single key'
            ' or list of lists, not: {}{}'
            .format(cfgname, cfgval, append_err)
        ))

    return _json_load_sublisted()

