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

import os

from configobj import ConfigObj, ConfigObjError

from ...helpers import dob_in_user_warning
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

    def _load_classes_style():
        named_style = resolve_named_style()
        classes_style = try_load_dict_from_user_styling(named_style)
        return instantiate_or_try_internal_style(named_style, classes_style)

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
        if named_style in config_obj:
            classes_style = config_obj[named_style]
            return classes_style
        return None


    def instantiate_or_try_internal_style(named_style, classes_style):
        if classes_style is not None:
            controller.affirm(isinstance(classes_style, dict))
            # Load various_styles.default to ensure all keys present,
            # then update that.
            defaults = various_styles.default()
            defaults._update_gross(classes_style)
            return defaults
        return load_internal_style(named_style)

    def load_internal_style(named_style):
        classes_style_fn = load_obj_from_internal(
            controller,
            obj_name=named_style,
            internal=various_styles,
            # HARDCODED/DEFAULT: classes_style default: 'color'.
            default_name='color',
            warn_tell_not_found=True,
        )
        # If None, Carousel will eventually set to a default of its choosing.
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
        compile_eval_rules(matches_style)
        return matches_style

    def compile_eval_rules(matches_style):
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
                msg = _("compile() failed on 'eval' from “{0}” in “{1}”").format(
                    section, stylit_path,
                )
                dob_in_user_warning(msg)

    # ***

    return _load_matches_style()


# ***

def create_configobj(conf_path, nickname=''):
    try:
        return ConfigObj(conf_path, write_empty_values=False)
    except ConfigObjError as err:
        # Catches DuplicateError, etc.
        # E.g., Parsing failed with several errors.
        #       First error at line 55.
        msg = _("failed to understand {0} config at “{1}”: {2}").format(
            nickname, conf_path, str(err),
        )
        dob_in_user_warning(msg)
        return {}

