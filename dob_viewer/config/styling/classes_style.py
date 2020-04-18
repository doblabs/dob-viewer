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

import os

from configobj import ConfigObj, ConfigObjError

from dob_bright.termio import dob_in_user_warning

from .. import pause_on_error_message_maybe

from . import load_obj_from_internal, various_styles

__all__ = (
    'load_classes_style',
    'load_matches_style',
    # PRIVATE:
    # 'create_configobj',
    'resolve_named_style',
)


def load_classes_style(controller, style_name=''):
    # (lb): It's times like these -- adding a dict to get around scoping
    # when sharing a variable -- that I think a method (load_classes_style)
    # should be a class. But this works for now.
    load_failed = {'styles': False}

    def _load_classes_style():
        named_style = style_name or resolve_named_style(controller.config)
        classes_dict = load_dict_from_styles_conf(named_style)
        classes_style = instantiate_or_try_internal_style(named_style, classes_dict)
        return classes_style

    def load_dict_from_styles_conf(named_style):
        styles_conf, failed = load_styles_conf(controller.config)
        if failed:
            load_failed['styles'] = True
            pause_on_error_message_maybe(controller.ctx)
        elif styles_conf and named_style in styles_conf:
            classes_dict = styles_conf[named_style]
            return classes_dict
        return None

    def instantiate_or_try_internal_style(named_style, classes_dict):
        if classes_dict is not None:
            controller.affirm(isinstance(classes_dict, dict))
            defaults = prepare_base_style(classes_dict)
            update_base_style(named_style, classes_dict, defaults)
            return defaults
        return load_internal_style(named_style)

    def prepare_base_style(classes_dict):
        # Load base-style (e.g., various_styles.default) to ensure
        # all keys present (and defaulted), and then update that.
        base_style = 'default'
        if 'base-style' in classes_dict:
            base_style = classes_dict['base-style'] or 'default'
        try:
            # This gets a StylesRoot object created by _create_style_object.
            defaults = getattr(various_styles, base_style)()
        except AttributeError as err:  # noqa: F841
            # Unexpected, because of choices= on base-style @setting def.
            controller.affirm(False)
            defaults = various_styles.default()
        return defaults

    def update_base_style(named_style, classes_dict, defaults):
        try:
            defaults.update_gross(classes_dict)
        except Exception as err:
            msg = _("Failed to load style named “{0}”: {1}").format(
                named_style, str(err),
            )
            dob_in_user_warning(msg)

    def load_internal_style(named_style):
        # HARDCODED/DEFAULT: classes_style default: 'default' (Ha!).
        # - This style uses no colors, so the UX will default to however
        #   the terminal already looks.
        default_style = 'default'
        classes_style_fn = load_obj_from_internal(
            controller,
            obj_name=named_style,
            internal=various_styles,
            default_name=default_style,
            warn_tell_not_found=not load_failed['styles'],
            config_key=CFG_KEY_ACTIVE_STYLE,
        )
        # If None, Carousel will eventually set to a default of its choosing.
        # - (lb): Except that we specified default_name, so never None:
        controller.affirm(classes_style_fn is not None)
        return classes_style_fn and classes_style_fn() or None

    # ***

    return _load_classes_style()


# ***

def load_styles_conf(config):
    """Return 2-tuple, the styles.conf ConfigObj, and a bool indicating failure.

    The config object will be None if the path does not exist, or if it failed to
    loaded. Failure will be False if the object was loaded, or if the path does
    not exists; failure is True if the file exists, but ConfigObj failed to load it.
    """
    def _load_styles_conf():
        styles_path = resolve_path_styles()
        if not os.path.exists(styles_path):
            return None, False
        return load_dict_from_user_styling(styles_path)

    def resolve_path_styles():
        cfg_key_fpath = 'editor.styles_fpath'
        return config[cfg_key_fpath]

    def load_dict_from_user_styling(styles_path):
        styles_conf = create_configobj(styles_path, nickname='styles')
        if styles_conf is None:
            return None, True
        return styles_conf, False

    return _load_styles_conf()


# ***

def load_matches_style(controller):
    config = controller.config

    def _load_matches_style():
        matches_style = try_load_dict_from_user_stylit()
        return matches_style

    def try_load_dict_from_user_stylit():
        stylit_path = resolve_path_stylit()
        if not os.path.exists(stylit_path):
            return None
        return load_dict_from_user_stylit(stylit_path)

    def resolve_path_stylit():
        cfg_key_fpath = 'editor.stylit_fpath'
        return config[cfg_key_fpath]

    def load_dict_from_user_stylit(stylit_path):
        matches_style = create_configobj(stylit_path, nickname='stylit')
        if matches_style is None:
            return None
        compile_eval_rules(matches_style, stylit_path)
        return matches_style

    def compile_eval_rules(matches_style, stylit_path):
        # Each section may optionally contain one code/eval component. Compile
        # it now to check for errors, with the bonus that it's cached for later
        # ((lb): not that you'd likely notice any change in performance with or
        # without the pre-compile).
        for section, rules in matches_style.items():
            if 'eval' not in rules:
                continue
            try:
                rules['__eval__'] = compile(
                    source=rules['eval'],
                    filename='<string>',
                    # Specifying 'eval' because single expression.
                    # Could use 'exec' for sequence of statements.
                    mode='eval',
                )
            except Exception as err:
                msg = _("compile() failed on 'eval' from “{0}” in “{1}”: {2}").format(
                    section, stylit_path, str(err),
                )
                dob_in_user_warning(msg)

    # ***

    return _load_matches_style()


# ***

def create_configobj(conf_path, nickname=''):
    try:
        return ConfigObj(
            conf_path,
            interpolation=False,
            write_empty_values=False,
        )
    except ConfigObjError as err:
        # Catches DuplicateError, and other errors, e.g.,
        #       Parsing failed with several errors.
        #       First error at line 55.
        msg = _("Failed to load {0} config at “{1}”: {2}").format(
            nickname, conf_path, str(err),
        )
        dob_in_user_warning(msg)
        return None


# ***

CFG_KEY_ACTIVE_STYLE = 'editor.styling'


def resolve_named_style(config):
    return config[CFG_KEY_ACTIVE_STYLE]

