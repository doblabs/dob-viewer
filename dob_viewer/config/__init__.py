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

# Add our settings to the config.
from .custom_paste import DobViewerConfigCustomPaste  # noqa: F401 '<>' imported ...
from .editor_keys import DobViewerConfigEditorKeys    # noqa: F401  ... but unused

from nark.config import ConfigRoot

__all__ = (
    'DobConfigurableDev',
)


# ***

@ConfigRoot.section('dev')
class DobConfigurableDev(object):
    """"""

    def __init__(self, *args, **kwargs):
        pass

    # ***

    @property
    @ConfigRoot.setting(
        _("If True, lets you quit without saving by mashing Ctrl-q."),
        hidden=True,
    )
    def allow_mash_quit(self):
        return False

