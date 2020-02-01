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

import re

__all__ = (
    'namilize',
)


# SYNC_ME: Use same re as PPT. From prompt_toolkit/styles/style.py::
#  CLASS_NAMES_RE = re.compile(r'^[a-z0-9.\s_-]*$')  # This one can't contain a comma!
# except that we need the regex for a substitution, i.e., drop the ^, *, and $.
CLASS_NAME_NOTSET = re.compile(r'[^a-z0-9.\s_-]')
# NOTE/2019-12-09: (lb) Spaces are allowed are class names. I'm not sure how works in
# practice. TESTME: one feature is making PPT tuples using act, cat, and tag names
# as class names. Can you customize such a name that has a space in it?


def namilize(name):
    """Normalizes a string so it can be used as a prompt_toolkit (PPT) classname.
    """
    return CLASS_NAME_NOTSET.sub('-', name.lower())

