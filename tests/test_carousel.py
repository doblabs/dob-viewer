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

import pytest

from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

from dob_viewer.crud.parse_input import parse_input
from dob_viewer.crud.save_confirmer import prompt_and_save_confirmer
from dob_viewer.ptkui import re_confirm


@pytest.fixture
def new_facts(controller_with_logging):
    input_stream = open(IMPORT_PATH, 'r')
    new_facts = parse_input(
        controller_with_logging,
        file_in=input_stream,
        progress=None,
    )
    return new_facts


IMPORT_PATH = './tests/fixtures/test-import-fixture.rst'
"""Path to the import file fixture, which is full of Factoids."""


class TestBasicCarousel(object):
    """Non-interactive Interactive Carousel tests."""

    # ***

    def _feed_cli_with_input(
        self,
        controller_with_logging,
        new_facts,
        key_sequence,
        mocker,
    ):
        # (lb): In the original tests, back when PTK2, we monkeypatch'ed sys,stdin
        # to a pipe opened from a pty.openpty pseudo terminal, which smelled very
        # fragile, and came with the caveat that Python's pty library probably
        # doesn't run well on non-Linux. Thankfully, PTK3 has a formal mechanism
        # for overriding I/O. See decent examples under prompt_toolkit/tests/.

        # The Carousel will prompt for confirmation on quit without having saved.
        re_confirm.confirm = mocker.MagicMock(return_value=True)

        inp = create_pipe_input()
        try:
            inp.send_text(key_sequence)
            # Ignoring return value: saved_facts.
            prompt_and_save_confirmer(
                controller_with_logging,
                edit_facts=new_facts,
                # Test apparatus.
                input=inp,
                output=DummyOutput(),
            )
        finally:
            inp.close()

    # ***

    @pytest.mark.parametrize(
        ('key_sequence'),
        [
            # *** test_basic_import4_left_arrow_three_time
            #
            # Test left-arrowing and first (early Life) gap fact.
            # Left arrow three times.
            # - First time creates and jumps to gap fact.
            # - Second time causes at-first-fact message.
            # - Third time's a charm.
            [
                '\x1bOD',   # Left arrow ←.
                '\x1bOD',   # Left arrow ←.
                '\x1bOD',   # Left arrow ←.
                '\x11',     # Ctrl-Q.
                '\x11',     # Ctrl-Q.
                '\x11',     # Ctrl-Q.
            ],

            # *** test_basic_import4_right_arrow_left_arrow
            #
            [
                # Arrow right, arrow left.
                '\x1bOD',
                '\x1bOC',
                # Three Cancels don't make a Right.
                '\x11',
                '\x11',
                '\x11',
                # FIXME/2019-02-20: Because, what, arrowing left goes to
                #                   Previous Big Bang Gap Fact,
                #                   so extra Ctrl-Q needed?
                #                   Oddly, in log, I still only see 2 exit_command's!
                #                   But apparently we need 4 strokes to exit.
                '\x11',
            ],

            # *** test_basic_import4_G_go_last
            [
                # Jump to final fact.
                'G',
                '\x11',
                '\x11',
                '\x11',
            ],
        ],
    )
    def test_basic_import4_left_arrow_three_time(
        self,
        controller_with_logging,
        new_facts,
        key_sequence,
        mocker,
    ):
        self._feed_cli_with_input(
            controller_with_logging,
            new_facts,
            ''.join(key_sequence),
            mocker,
        )

