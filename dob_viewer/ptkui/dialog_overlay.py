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

# AUTHOR: Parts of this file copied from PTK sources, by Jonathan Slenders.
#   https://github.com/prompt-toolkit/python-prompt-toolkit
#     examples/full-screen/text-editor.py
#   Wholly: class MessageDialog, and function show_dialog_as_float.
#   Partially: function show_message.
#
# LICENSE:
#   Copyright (c) 2014, Jonathan Slenders
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without modification,
#   are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright notice, this
#     list of conditions and the following disclaimer in the documentation and/or
#     other materials provided with the distribution.
#
#   * Neither the name of the {organization} nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#   ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#   WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
#   ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#   (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#   LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#   ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#   SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""""""

from gettext import gettext as _

from asyncio import ensure_future, Future

from prompt_toolkit.application.current import get_app
from prompt_toolkit.layout.containers import Float, HSplit
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.widgets import Button, Dialog, Label

__all__ = (
    'alert_and_question',
    'show_message',
    # Private:
    #   'AlertResponseDialog',
    #   'MessageDialog',
    #   'show_dialog_as_float',
)


def show_message(root_container, title, text):
    async def coroutine():
        dialog = MessageDialog(title, text)
        await ensure_future(show_dialog_as_float(root_container, dialog))

    ensure_future(coroutine())


# ***

class MessageDialog(object):
    def __init__(self, title, text):
        self.future = Future()

        def set_done():
            self.future.set_result(None)

        ok_button = Button(text=_('OK'), handler=(lambda: set_done()))

        self.dialog = Dialog(
            title=title,
            body=HSplit([
                Label(text=text),
            ]),
            buttons=[ok_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


async def show_dialog_as_float(root_container, dialog):
    " Coroutine. "
    float_ = Float(content=dialog)
    root_container.floats.insert(0, float_)

    app = get_app()

    focused_before = app.layout.current_window
    app.layout.focus(dialog)
    result = await dialog.future
    app.layout.focus(focused_before)

    if float_ in root_container.floats:
        root_container.floats.remove(float_)

    return result


# ***

class AlertResponseDialog(object):
    def __init__(self, title='', label_text='', prompt_ok='', prompt_no=''):
        # MAGIC_NUMBER: 4: Pad button label so appears padded ``< LIKE SO >``
        BUTTON_PADDING = 4

        self.future = Future()

        def accept_text(buffer):
            get_app().layout.focus(button_ok)
            self.text_area.buffer.complete_state = None

        def on_button_ok():
            self.future.set_result(True)

        def on_button_no():
            self.future.set_result(False)

        button_ok = Button(
            text=prompt_ok,
            handler=on_button_ok,
            width=(len(prompt_ok) + BUTTON_PADDING),
        )
        button_no = Button(
            text=prompt_no,
            handler=on_button_no,
            width=(len(prompt_no) + BUTTON_PADDING),
        )

        self.dialog = Dialog(
            title=title,
            body=HSplit([
                Label(text=label_text),
            ]),
            buttons=[button_ok, button_no],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


def alert_and_question(
    root_container,
    title='',
    label_text='',
    prompt_ok=_('OK'),
    prompt_no=_('Cancel'),
    on_close=lambda x: None,
):
    async def coroutine():
        ar_dialog = AlertResponseDialog(
            title=title,
            label_text=label_text,
            prompt_ok=prompt_ok,
            prompt_no=prompt_no,
        )
        result = await show_dialog_as_float(root_container, ar_dialog)
        on_close(result)

    ensure_future(coroutine())

