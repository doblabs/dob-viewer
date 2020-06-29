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

import pytest

# When dob was split into Packages of Four, all the fixtures were sent to
# dob-bright. Import those fixtures into the test namespace with a *-glob,
# just as though they'd be defined in this module.
from dob_bright.tests.conftest import *  # noqa: F401, F403

from dob_bright.crud.fact_dressed import FactDressed


@pytest.fixture
def test_fact_cls():
    return FactDressed

