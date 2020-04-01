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

"""``hamster``, ``hamster``, ``hamster``!!! a cuddly, furry time tracker."""

import os
import sys

__all__ = (
    'get_version',
    '__arg0name__',
    '__package_name__',
)

# Note that this package is a library, so __arg0name__ likely, e.g., 'dob'.
__arg0name__ = os.path.basename(sys.argv[0])

__package_name__ = 'dob-viewer'


def get_version(include_head=False):
    # HEH?/2020-04-01: (lb): I had to move this import in here, otherwise
    # `tox -e docs` says cannot find 'nark'. Does not affect other projects,
    # even though if you diff against, e.g., dob-prompt, there's no difference
    # between the tox.ini setup, nor setup.py. But on dob-prompt, I see all
    # projects from setup.py installed, but not for dob-viewer. IDGI!
    from nark import get_version as _get_version

    return _get_version(ref_file=__file__, include_head=include_head)

