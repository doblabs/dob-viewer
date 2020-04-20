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

"""dob_viewer.config sub.package provides Carousel UX user configuration settings."""

import json
import time

from gettext import gettext as _

from config_decorator.config_decorator import ConfigDecorator

from dob_bright.config.fileboss import create_configobj

# Add our settings to the config.
from .custom_paste import DobViewerConfigCustomPaste  # noqa: F401 '<>' imported ...
from .editor_keys import DobViewerConfigEditorKeys    # noqa: F401  ... but unused

__all__ = (
    'decorate_and_wrap',
    'json_load_keycodes',
    'pause_on_error_message_maybe',
)


# ***

def decorate_and_wrap(section_name, classes_style, complete=False):
    def _decorate_and_wrap():
        # Sink the section once so we can get ConfigObj to print
        # the leading [section_name].
        condec = ConfigDecorator.create_root_for_section(section_name, classes_style)
        return wrap_in_configobj(condec, complete=complete)

    def wrap_in_configobj(condec, complete=False):
        config_obj = create_configobj(conf_path=None)
        # Set skip_unset so none of the default values are spit out (keeps the
        # config more concise); and set keep_empties so empty sections are spit
        # out (so, e.g., `[default]` at least appears).
        config_obj.merge(condec.as_dict(
            skip_unset=not complete,
            keep_empties=not complete,
        ))
        return config_obj

    return _decorate_and_wrap()


# ***

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


# ***

def pause_on_error_message_maybe(ctx=None):
    if not ctx or ctx.command.name == 'edit':
        time.sleep(2.666)

