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
from unittest.mock import Mock

# Import the Application object, though unreferenced, for monkeypatch to work.
from prompt_toolkit.application.application import Application  # noqa: F401
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

from dob.helpers import re_confirm
from dob.transcode import import_facts


IMPORT_PATH = './tests/fixtures/test-import-fixture.rst'
"""Path to the import file fixture, which is full of Factoids."""


class TestBasicCarousel(object):
    """Non-interactive Interactive Carousel tests."""

    # ***

    def _feed_cli_with_input(
        self, controller_with_logging, key_sequence, mocker, monkeypatch,
    ):
        # (lb): In the original tests, back when PTK2, we monkeypatched sys,stdin
        # to a pipe opened from a pty.openpty pseudo terminal, which smelled very
        # fragile, and came with the caveat that Python's pty library probably
        # doesn't run well on non-Linux. Thankfully, PTK3 has a formal mechanism
        # for overriding I/O. See decent examples under prompt_toolkit/tests/.

        re_confirm.confirm = mocker.MagicMock(return_value=True)

        inp = create_pipe_input()
        input_stream = open(IMPORT_PATH, 'r')
        try:
            inp.send_text(key_sequence)
            import_facts(
                controller_with_logging,
                file_in=input_stream,
                file_out=None,
                use_carousel=True,
                force_use_carousel=True,

                input=inp,
                output=DummyOutput(),
            )
        finally:
            inp.close()

    # ***

    @pytest.mark.parametrize(
        ('key_sequence'),
        [
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
        ],
    )
    def test_basic_import4_left_arrow_three_time(
        self, controller_with_logging, key_sequence, mocker, monkeypatch,
    ):
        self._feed_cli_with_input(
            controller_with_logging, ''.join(key_sequence), mocker, monkeypatch,
        )

    # ***

    @pytest.mark.parametrize(
        ('key_sequence'),
        [
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
                #                   Oddly, in log, I still only see 2 cancel_command's!
                #                   But apparently we need 4 strokes to exit.
                '\x11',
            ],
        ],
    )
    def test_basic_import4_right_arrow_left_arrow(
        self, controller_with_logging, key_sequence, mocker, monkeypatch
    ):
        self._feed_cli_with_input(
            controller_with_logging, ''.join(key_sequence), mocker, monkeypatch,
        )

    # ***

    @pytest.mark.parametrize(
        ('key_sequence'),
        [
            [
                # Jump to final fact.
                'G',
                '\x11',
                '\x11',
                '\x11',
            ],
        ],
    )
    def test_basic_import4_G_go_last(
        self, controller_with_logging, key_sequence, mocker, monkeypatch,
    ):
        self._feed_cli_with_input(
            controller_with_logging, ''.join(key_sequence), mocker, monkeypatch,
        )

