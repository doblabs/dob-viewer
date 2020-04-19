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

"""Prints styles and stylit config to stdout to help user setup custom styling."""

import os
import tempfile

from gettext import gettext as _

from config_decorator.config_decorator import ConfigDecorator

from dob_bright.termio import click_echo, dob_in_user_warning

from .classes_style import (
    create_configobj,
    load_classes_style,
    load_styles_conf,
    resolve_path_styles
)
from .various_styles import KNOWN_STYLES

__all__ = (
    'print_styles_conf',
)


def print_styles_conf(controller, style_name='', internal=False, complete=False):
    """Prints style config section(s) from styles.conf or internal sources.
    """
    config = controller.config

    def _print_styles_conf():
        if not internal:
            config_obj = load_config_obj()
        else:
            config_obj = load_style_conf()
        if config_obj:
            print_result(config_obj)
        # Else, already printed error message.

    # ***

    def load_config_obj():
        config_obj, failed = load_styles_conf(config)
        if config_obj:
            return filter_config_obj(config_obj)
        if failed:
            # load_styles_conf prints a ConfigObj error message. Our job is done.
            return None
        return echo_error_no_styles_conf()

    def filter_config_obj(config_obj):
        if not style_name:
            return config_obj
        new_config = create_configobj(conf_path=None)
        try:
            new_config.merge({style_name: config_obj[style_name]})
        except KeyError:
            return echo_error_no_styles_section()
        else:
            return new_config

    def echo_error_no_styles_conf():
        msg = _("No styles.conf found at: {0}").format(resolve_path_styles(config))
        dob_in_user_warning(msg)
        return None

    def echo_error_no_styles_section():
        msg = _("No matching section “{0}” found in styles.conf at: {1}").format(
            style_name, resolve_path_styles(config),
        )
        dob_in_user_warning(msg)
        return None

    # ***

    def load_style_conf():
        if style_name:
            return load_single_style()
        return load_known_styles()

    def load_single_style():
        classes_style = load_classes_style(controller, style_name, skip_default=True)
        if not classes_style:
            # load_obj_from_internal will have output a warning message.
            return None
        return decorate_and_wrap(classes_style)

    def decorate_and_wrap(classes_style):
        # Sink the section once so we can get ConfigObj to print
        # the leading [style_name].
        styles_conf = ConfigDecorator(object, cls_or_name='', parent=None)
        styles_conf.set_section(style_name, classes_style)
        return wrap_in_configobj(styles_conf, complete)

    def load_known_styles():
        """Adds all internal styles to a configobj.

        Includes all settings for the first style ('default'), but only
        those settings that are explicitly set for the remaining styles.
        """
        config_obj = create_configobj(conf_path=None)
        is_default = True
        for name in KNOWN_STYLES:
            classes_style = load_classes_style(controller, name, skip_default=True)
            styles_conf = ConfigDecorator(object, cls_or_name='', parent=None)
            styles_conf.set_section(name, classes_style)
            config_obj.merge(styles_conf.as_dict(
                skip_unset=not is_default and not complete,
                keep_empties=not is_default and not complete,
            ))
            is_default = False
        return config_obj

    # ***

    def print_result(config_obj):
        temp_f = prepare_temp_file(config_obj)
        write_styles_conf(config_obj)
        open_and_print_dump(temp_f)

    def prepare_temp_file(config_obj):
        # Not that easy:
        #   config_obj.filename = sys.stdout
        # (lb): My understanding is that for the TemporaryFile to be openable
        # on Windows, we should close it first (Linux can open an opened file
        # again, but not Windows).
        #   https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile
        temp_f = tempfile.NamedTemporaryFile(delete=False)
        temp_f.close()
        config_obj.filename = temp_f.name
        return temp_f

    def write_styles_conf(config_obj):
        config_obj.write()

    def open_and_print_dump(temp_f):
        with open(temp_f.name, 'r') as fobj:
            click_echo(fobj.read().strip())
        os.unlink(temp_f.name)

    return _print_styles_conf()


# ***

def wrap_in_configobj(styles_conf, complete=False):
    config_obj = create_configobj(conf_path=None)
    # Set skip_unset so none of the default values are spit out (keeps the
    # config more concise); and set keep_empties so empty sections are spit
    # out (so, e.g., `[default]` at least appears).
    config_obj.merge(styles_conf.as_dict(
        skip_unset=not complete,
        keep_empties=not complete,
    ))
    return config_obj

