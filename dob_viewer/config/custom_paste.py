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

from gettext import gettext as _

from nark.config import ConfigRoot

__all__ = (
    'DobViewerConfigCustomPaste',
)


# ***

@ConfigRoot.section('custom-paste')
class DobViewerConfigCustomPaste(object):
    """"""

    def __init__(self, *args, **kwargs):
        pass

    # ***

    # (lb): This is the best I've got on a moment's thought:
    # Create placeholder config so that it'll be read from user's dob.conf.
    # (lb): This is not the cleanest solutions (we have to arbitrarily decide how
    # many placeholders to create), but it's otherwise transparent to the user.

    def add_custom_paste(postfix):
        """"""
        factoid_name = 'factoid_{}'.format(postfix)
        mapping_name = 'mapping_{}'.format(postfix)

        @property
        @ConfigRoot.setting(
            _("XXX"),
            name=factoid_name,
            hidden=True,
        )
        def factoid_prop(self):
            return ''

        @property
        @ConfigRoot.setting(
            _("XXX"),
            name=mapping_name,
            hidden=True,
        )
        def mapping_prop(self):
            return ''

    A_PERFECT_NUMBER = 28

    for postfix in range(1, A_PERFECT_NUMBER):
        add_custom_paste(postfix)

