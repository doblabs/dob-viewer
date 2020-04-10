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

from ...traverser import various_styles
from . import load_obj_from_internal

__all__ = (
    'load_classes_style',
    'load_matches_style',
    # PRIVATE:
    # 'create_configobj',
)


def load_classes_style(controller):
    config = controller.config

    # (lb): It's times like these -- adding a dict to get around scoping
    # when sharing a variable -- that I think a method (load_classes_style)
    # should be a class. But this works for now.
    load_failed = {'styles': False}

    def _load_classes_style():
        named_style = resolve_named_style()
        classes_dict = try_load_dict_from_user_styling(named_style)
        classes_style = instantiate_or_try_internal_style(named_style, classes_dict)
        return classes_style

    def resolve_named_style():
        cfg_key_style = 'editor.styling'
        return config[cfg_key_style]

    def try_load_dict_from_user_styling(named_style):
        styles_path = resolve_path_styles()
        if not os.path.exists(styles_path):
            return None
        return load_dict_from_user_styling(styles_path, named_style)

    def resolve_path_styles():
        cfg_key_fpath = 'editor.styles_fpath'
        return config[cfg_key_fpath]

    def load_dict_from_user_styling(styles_path, named_style):
        config_obj = create_configobj(styles_path, nickname='styles')
        if config_obj is None:
            load_failed['styles'] = True
        elif named_style in config_obj:
            classes_dict = config_obj[named_style]
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
        )
        # If None, Carousel will eventually set to a default of its choosing.
        # - (lb): Except that we specified default_name, so never None:
        controller.affirm(classes_style_fn is not None)
        return classes_style_fn and classes_style_fn() or None

    # ***

    return _load_classes_style()


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

