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

from gettext import gettext as _

from nark.config import ConfigRoot

__all__ = (
    'DobConfigurableEditorKeys',
)


# ***

@ConfigRoot.section('editor-keys')
class DobViewerConfigurableDev(object):
    """"""

    def __init__(self, *args, **kwargs):
        pass

    # ***

    @property
    @ConfigRoot.setting(
        _("Switch to Next Widget (description → start time → end time → [repeats])"),
    )
    def focus_next(self):
        return 'tab'

    # ***

    @property
    @ConfigRoot.setting(
        _("Switch to Previous Widget (description → end time → start time → [repeats])"),
    )
    def focus_previous(self):
        return 's-tab'

    # ***

    @property
    @ConfigRoot.setting(
        _("Toggle To/From Start Time Widget"),
    )
    def edit_time_start(self):
        return 's'

    # ***

    @property
    @ConfigRoot.setting(
        _("Toggle To/From End Time Widget"),
    )
    def edit_time_end(self):
        return 'e'

    # ***

    @property
    @ConfigRoot.setting(
        _("Save Changes"),
    )
    def save_edited_and_live(self):
        return 'c-s'

    # ***

    @property
    @ConfigRoot.setting(
        _("Save Changes and Exit"),
    )
    def save_edited_and_exit(self):
        return 'c-w'

    # ***

    @property
    @ConfigRoot.setting(
        _("Exit Quietly if No Changes"),
    )
    def cancel_softly(self):
        return 'q'

    # ***

    @property
    @ConfigRoot.setting(
        _("Exit with Prompt if Changes"),
    )
    def cancel_command(self):
        return 'c-q'

