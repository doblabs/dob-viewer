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
"""Facts Carousel Custom User (Pygment-defined) Styles."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

from nark.config.inify import section
from nark.config.subscriptable import Subscriptable

__all__ = (
    'default',

    'color',
    'light',
    'night',

    'StylesRoot',
    'CustomStyling',
)


def create_style_object():
    """Define and return a ConfigDecorator for ~/.config/dob/styling/styles.conf."""

    # (lb): We want to wrap the @setting decorator (aka decorate the decorator),
    # which means we need to use two classes -- one to define the decorator, and
    # another that can call the decorator after the first class has been defined.

    @section(None)
    class StylesRoot(object):
        """"""

        def __init__(self):
            pass

        # ***

        NOT_STYLE_CLASSES = set()

        @classmethod
        def setting_wrap(cls, *args, not_a_style=False, **kwargs):
            def decorator(func):
                name = kwargs.get('name', func.__name__)
                if not_a_style:
                    cls.NOT_STYLE_CLASSES.add(name)
                return StylesRoot.setting(*args, **kwargs)(func)
            return decorator

        @classmethod
        def collect_tups(cls):
            style_classes = [
                (key, val.value) for key, val in StylesRoot._key_vals.items()
                if key not in cls.NOT_STYLE_CLASSES
            ]
            return style_classes

    # Now that the @section re-decorator is defined, we declare a class that
    # uses it to build a settings config. Note that we use a little @section
    # decorator magic on this second class -- by using a falsey section name,
    # in @StylesRoot.section(None), it causes CustomStyling to just be an
    # alias to StylesRoot! Which is the root config, so the settings defined
    # in CustomStyling will be added to the root config, and not to a
    # sub-section. Somewhat wonky, but wonky is our jam.

    # (lb): 2 hacks here, because of the eccentric magic of the @section
    # and ConfigDecorator:
    # 1.) We wrap @ConfigDecorator.setting so we can identify which of our
    #     key-value settings are "class:..." assignments, and which of our
    #     key-value settings are the rules to decide if the class assignments
    #     should be applied.
    #     - The reason we mix the two types of settings in the same config
    #     section, rather than using two separate section, is to keep the
    #     config flat and simple. It helps minimize the types of errors the
    #     user can make while editing their stylit.conf file.
    #     - The hack is reaching into StylesRoot (which is also a hack: it's
    #     not a class, but an object instance! because of the eccentric magic
    #     of @section) and finding our @setting_wrap through the special
    #     _innerobj attribute.
    # 2.) Hack number two here is specifying a `None` @section when defining
    #     the CustomStyling class, so that the @setting decorator applies each
    #     setting to the root config, and not to a sub-section.
    #     - I.e., each setting herein will be applied to the StylesRoot object.
    #     In fact, CustomStyling disappears, in a sense, because the decorator
    #     returns the section to which the class settings apply, so you'll find:
    #       assert(CustomStyling is StylesRoot)  # Totally crazy, I know!
    # 3.) I suppose there's actually a third hack, or maybe it's a trick, or just
    #     The Way To Do It: we use the encompassing create_style_object() method
    #     to localize the defined classes/objects (StylesRoot and CustomStyling)
    #     so that we don't end up creating singletons, but rather create unique
    #     config objects each time.

    setting = StylesRoot._innerobj.setting_wrap

    @StylesRoot.section(None)
    class CustomStyling(Subscriptable):
        """"""

        def __init__(self):
            pass

        # ***

        @property
        @setting(
            _("Generated value."),
            hidden=True,
            not_a_style=True,
        )
        def collect_tups(self):
            return StylesRoot._innerobj.collect_tups()

        # ***

        @property
        @setting(
            _("If True, center interactive editor in terminal; otherwise justify left."),
            name='editor-align',
            not_a_style=True,
        )
        def editor_align(self):
            return 'LEFT'

        # ***

        @property
        @setting(
            _("Maximum height, in terminal rows, of the Fact description control."),
            name='content-height',
            not_a_style=True,
        )
        def content_height(self):
            return 10

        # ***

        @property
        @setting(
            _("Maximum width, in terminal columns, of the Fact description control."),
            name='content-width',
            not_a_style=True,
        )
        def content_width(self):
            return 90

        # ***

        @property
        @setting(
            _("If True, wrap the Fact description text; otherwise, scroll horizontally."),
            name='content-wrap',
            not_a_style=True,
        )
        def content_wrap(self):
            return True

        # ***

        @property
        @setting(
            _("Default style of the streamer UX banner (topmost UX)."),
            name='header-help',
            # NOTE: (lb): Not a style in that code sets directly on widget,
            #       using (style, text) tuple, bypassing "class:" styling.
            not_a_style=True,
        )
        def header_help(self):
            return 'bg:#000000 #FFFFFF bold'

        # ***

        @property
        @setting(
            _("Default style when showing Fact description in content area."),
            name='content-area',
        )
        def content_area(self):
            return 'bg:#000000 #FFFFFF'

        # ***

        @property
        @setting(
            _("Default style when showing help in the content area."),
            name='content-help',
        )
        def content_help(self):
            return 'bg:#000000 #FFFFFF'

        # ***

        @property
        @setting(
            _("Style of content area when showing a generated, unsaved gap Fact."),
            name='interval-gap',
        )
        def interval_gap(self):
            return 'bg:#000000 #FFFFFF'

        # ***

        @property
        @setting(
            _("Style of content area when showing an edited, unsaved Fact."),
            name='unsaved-fact',
        )
        def unsaved_fact(self):
            return 'bg:#000000 #FFFFFF'

        # ***

        @property
        @setting(
            _("Style of time widget when focused and editable."),
            name='header-focus',
        )
        def header_focus(self):
            # EXPLAIN/2019-12-04: (lb): I'm not sure I've seen this style WAD.
            return 'bg:#00FFFF #0000FF'

    return StylesRoot


# ***

def default():
    """Default defines all options so tweaked stylings may omit any."""

    # (lb): Because of the magic of @section and how CustomStyling is not
    # really a class, but rather a ConfigDecorator object, we use a wrapper
    # function to both define the config (every time it's called) and to
    # return the newly instantiated ConfigDecorator object (which can only
    # be accessed using the name of the @section-decorated class!).

    styling = create_style_object()

    return styling


def color():
    styling = default()

    styling['editor-align'] = 'JUSTIFY'

    styling['header-help'] = 'fg:#5F5FFF bold'

    # Loosely based on such and such color palette:
    #
    #   http://paletton.com/#uid=3000u0kg0qB6pHIb0vBljljq+fD

    # Default Fact.description frame background.
    styling['content-area'] = 'bg:#9BC2C2 #000000'

    # Fact.description background when showing help.
    styling['content-help'] = 'bg:#66AAAA #000000'

    # Other contextual Fact.description background colors.
    styling['interval-gap'] = 'bg:#AA6C39 #000000'
    styling['unsaved-fact'] = 'bg:#D0EB9A #000000'

    styling['header-focus'] = 'bg:#00FFFF #0000FF'

    return styling


def light():
    styling = default()

    styling['editor-align'] = 'LEFT'

    styling['header-help'] = 'bg:#FFFFFF #000000 bold'
    styling['content-area'] = 'bg:#FFFFFF #000000'
    styling['content-help'] = 'bg:#FFFFFF #000000'
    styling['interval-gap'] = 'bg:#FFFFFF #000000'
    styling['unsaved-fact'] = 'bg:#FFFFFF #000000'

    return styling


def night():
    styling = default()

    styling['editor-align'] = 'LEFT'

    styling['header-help'] = 'bg:#000000 #FFFFFF bold'
    styling['content-area'] = 'bg:#000000 #FFFFFF'
    styling['content-help'] = 'bg:#000000 #FFFFFF'
    styling['interval-gap'] = 'bg:#000000 #FFFFFF'
    styling['unsaved-fact'] = 'bg:#000000 #FFFFFF'

    return styling

