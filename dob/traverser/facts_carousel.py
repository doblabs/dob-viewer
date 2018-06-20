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
"""Facts Carousel"""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

import asyncio
import click  # Only for get_terminal_size.

from prompt_toolkit.application import Application
from prompt_toolkit.eventloop import use_asyncio_event_loop
from prompt_toolkit.filters import Always, Never
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import HSplit, Layout
from prompt_toolkit.layout.containers import to_container
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Box, Frame, Label, TextArea

from ..interrogate import ask_user_for_edits
from ..helpers.re_confirm import confirm
from ..prompters.interface_bonds import KeyBond

__all__ = [
    'FactsCarousel',
]


class FactsCarousel(object):
    """"""
    def __init__(
        self,
        controller,
        new_facts,
        raw_facts,
        backup_callback,
        dry,
    ):
        self.controller = controller
        self.new_facts = new_facts
        self.raw_facts = raw_facts
        self.backup_callback = backup_callback
        self.dry = dry

        self.curx = 0
        self.user_seen_all = False

        # FIXME: make height configurable
        self.scrollable_height = 10

        # (lb): This doesn't need to run async, but maybe in the future?
        # In fact, you shouldn't see any runtime difference except in the
        # event an exception is raised, and then sometimes, after the our
        # error handlers are the exception continues to raise, you half the
        # time see additional output (but not always), such as:
        #   Exception ignored in: <bound method BaseEventLoop.__del__
        #       of <_UnixSelectorEventLoop running=False closed=True debug=False>>
        #   Traceback (most recent call last):
        #     File "/usr/lib/python3.5/asyncio/base_events.py", line 431, in __del__
        #     File "/usr/lib/python3.5/asyncio/unix_events.py", line 58, in close
        #     File ".../asyncio/unix_events.py", line 139, in remove_signal_handler
        #     File "/usr/lib/python3.5/signal.py", line 47, in signal
        #   TypeError: signal handler must be signal.SIG_IGN, signal.SIG_DFL,
        #       or a callable object
        self.async_enable = True

    def gallop(self):
        self.stand_up()
        confirmed_facts = self.run_edit_loop()
        return confirmed_facts

    def run_edit_loop(self):
        confirmed_facts = False
        used_prompt = None
        self.enduring_edit = True
        while self.enduring_edit:
            self.runloop()
            if not self.confirm_exit:
                if self.enduring_edit:
                    used_prompt = self.prompt_fact_edits(used_prompt)
                elif not self.user_seen_all:
                    confirmed = self.process_save_early()
                    if confirmed:
                        confirmed_facts = True
                    else:
                        self.enduring_edit = True  # Keep looping.
            if self.confirm_exit:
                confirmed = self.process_exit_request()
                if not confirmed:
                    self.enduring_edit = True  # Keep looping.
            elif not self.enduring_edit:
                confirmed_facts = True  # All done; user looked at all Facts.
        return confirmed_facts

    def process_exit_request(self):
        question = _('\nReally exit without saving?')
        confirmed = confirm(question, erase_when_done=True)
        return confirmed

    def process_save_early(self):
        question = _('\nReally save without verifying all Facts?')
        confirmed = confirm(question, erase_when_done=True)
        return confirmed

    def prompt_fact_edits(self, used_prompt):
        try:
            used_prompt = self.user_prompt_edit_fact(used_prompt)
        except KeyboardInterrupt as err:
            self.enduring_edit = False
            self.confirm_exit = True
        return used_prompt

    def user_prompt_edit_fact(self, used_prompt):
        used_prompt = ask_user_for_edits(
            self.controller,
            self.curr_fact,
            always_ask=True,
            prompt_agent=used_prompt,
            restrict_edit=self.restrict_edit,
        )
        self.backup_callback()
        self.refresh_fact()
        return used_prompt

    def stand_up(self):
        self.prepare_first_fact()
        self.setup_scrollable()
        self.assemble_application()
        self.refresh_fact()

    def prepare_first_fact(self):
        if len(self.new_facts) > 0:
            self.curx = 0
            self.curr_fact = self.new_facts[self.curx]
        else:
            # FIXME: Showing existing Facts a WIP.
            self.curx = -1
            self.curr_fact = self.controller.antecedent()  # ref_time=controller.now())

    def setup_scrollable(self):
        # Layout for displaying Fact description.
        # The Frame creates the border.
        self.content = TextArea(
            text='',
            read_only=True,
            focusable=True,  # Unnecessary; included for completeness.
            # Without the - 2, to account for the '|' borders, hangs.
            width=click.get_terminal_size()[0] - 2,
            height=self.scrollable_height,
        )
        self.scrollable = Frame(
            self.content,
            # title="Fact Description",
            style='class:content-area',
        )

    def assemble_application(self):
        self.root = self.build_root_container()
        self.layout = self.build_application_layout()
        self.style = self.build_style_lookup()
        self.key_bindings = self.setup_key_bindings()
        self.application = self.build_application_object()

    def build_root_container(self):
        self.header_posit = 0
        self.footer_posit = 2
        self.hsplit = HSplit([
            self.assemble_header(),
            self.scrollable,
            self.assemble_footer(),
        ])
        root_container = Box(self.hsplit)
        return root_container

    def assemble_header(self, header_text=''):
        return Label(
            text=header_text,
            style='class:header',
        )

    def assemble_footer(self, footer_text=''):
        return Label(
            text=footer_text,
            style='class:footer',
        )

    def build_application_layout(self):
        layout = Layout(
            container=self.root,
            # Setting focused_element seems unnecessary for our particular layout.
            focused_element=self.scrollable,
        )
        return layout

    def build_style_lookup(self):
        style = Style([
            ('header-label', 'bg:#888800 #000000'),
            ('content-area', 'bg:#00aa00 #000000'),
        ])
        return style

    def setup_key_bindings(self):
        return self.setup_key_bindings_view_only()

    def setup_key_bindings_view_only(self):
        key_bindings = KeyBindings()

        clack_j = KeyBond('j', brief=_('bwd'), action=self.scroll_left)
        clack_k = KeyBond('k', brief=_('fwd'), action=self.scroll_right)
        clack_h = KeyBond('h', brief=None, action=self.cursor_up_one)
        clack_l = KeyBond('l', brief=None, action=self.cursor_down_one)
        # FIXME: (lb): Make (e) toggle inline editing...
        clack_e = KeyBond('e', brief=_('edit:'), action=self.edit_fact)
        clack_a = KeyBond('a', brief=_('-act.'), action=self.edit_actegory)
        clack_t = KeyBond('t', brief=_('-tags'), action=self.edit_tags)
        clack_d = KeyBond('d', brief=_('-descrip'), action=self.edit_description)
        ctrl_c = KeyBond('c-c', brief=_('quit'), action=self.cancel_command)
        # (lb): Be default, Ctrl-q is wired to something else, maybe a Readline-ish
        # function. In my experience, pressing it changes the cursor to the caret, ^,
        # and then I cannot get out of that state; I gotta `killall dob` to recover.
        # So map it to canceling.
        ctrl_q = KeyBond('c-q', None, action=self.cancel_command)
        ctrl_s = KeyBond('c-s', brief=_('save'), action=self.finish_command)
        page_up = KeyBond('pageup', brief=None, action=self.scroll_up)
        page_down = KeyBond('pagedown', brief=None, action=self.scroll_down)
        arrow_left = KeyBond(Keys.Left, brief=None, action=self.scroll_left)
        arrow_right = KeyBond(Keys.Right, brief=None, action=self.scroll_right)

        # The order here is the order used in the footer help.
        self.key_bonds = []
        self.key_bonds.append(clack_j)
        self.key_bonds.append(clack_k)
        self.key_bonds.append(clack_h)
        self.key_bonds.append(clack_l)
        self.key_bonds.append(clack_e)
        self.key_bonds.append(clack_a)
        self.key_bonds.append(clack_d)
        self.key_bonds.append(clack_t)
        self.key_bonds.append(ctrl_c)
        self.key_bonds.append(ctrl_q)
        self.key_bonds.append(ctrl_s)
        self.key_bonds.append(page_up)
        self.key_bonds.append(page_down)
        self.key_bonds.append(arrow_left)
        self.key_bonds.append(arrow_right)

        for keyb in self.key_bonds:
            key_bindings.add(keyb.keycode)(keyb.action)

        return key_bindings

    def build_application_object(self):
        application = Application(
            layout=self.layout,
            key_bindings=self.key_bindings,
            full_screen=False,
            erase_when_done=True,
            # Enables mouse wheel scrolling.
            # But steals from terminal app!
            mouse_support=True,
            style=self.style,
        )
        return application

    def runloop(self):
        self.confirm_exit = False
        self.enduring_edit = False
        self.restrict_edit = ''
        if self.async_enable:
            # Tell prompt_toolkit to use asyncio.
            use_asyncio_event_loop()
            # Run application async.
            asyncio.get_event_loop().run_until_complete(
                self.application.run_async().to_asyncio_future(),
            )
        else:
            self.application.run()

    def cancel_command(self, event):
        """"""
        self.confirm_exit = True
        event.app.exit()

    def finish_command(self, event):
        """"""
        event.app.exit()

    def scroll_left(self, event):
        """"""
        self.decrement()
        self.reset_cursor_left_column()

    def scroll_right(self, event):
        """"""
        self.increment()
        self.reset_cursor_left_column()

    def edit_fact(self, event):
        """"""
        self.enduring_edit = True
        event.app.exit()

    def edit_actegory(self, event):
        """"""
        self.enduring_edit = True
        self.restrict_edit = 'actegory'
        event.app.exit()

    def edit_tags(self, event):
        """"""
        self.enduring_edit = True
        self.restrict_edit = 'tags'
        event.app.exit()

    def edit_description(self, event):
        """"""
        self.enduring_edit = True
        self.restrict_edit = 'description'
        event.app.exit()

    def cursor_up_one(self, event):
        """"""
        self.content.buffer.cursor_up(1)

    def cursor_down_one(self, event):
        """"""
        self.content.buffer.cursor_down(1)

    def scroll_down(self, event):
        """"""
        self.content.buffer.cursor_down(self.scrollable_height - 1)
        self.reset_cursor_left_column()

    def scroll_up(self, event):
        """"""
        self.content.buffer.cursor_up(self.scrollable_height - 1)
        self.reset_cursor_left_column()

    def reset_cursor_left_column(self):
        self.content.buffer.cursor_left(
            # PPT returns a relative distance, e.g., -7, or 0 if already there.
            # A similar command, get_cursor_left_position(), return -1 or 0.
            -self.content.buffer.document.get_start_of_line_position()
        )

    def decrement(self):
        """"""
        prev_fact = None
        if self.curx > 0:
            self.curx -= 1
            prev_fact = self.new_facts[self.curx]
        else:
            self.curx = -1
            prev_fact = self.controller.facts.antecedent(self.curr_fact)
        if prev_fact is None:
            return
        self.refresh_fact(prev_fact)

    def increment(self):
        """"""
        next_fact = None
        if self.curx == -1:
            next_fact = self.controller.facts.subsequent(self.curr_fact)
        if next_fact is None:
            if (self.curx + 1) < len(self.new_facts):
                self.curx += 1
                next_fact = self.new_facts[self.curx]
        if next_fact is None:
            return
        self.refresh_fact(next_fact)

    def refresh_fact(self, show_fact=None):
        """"""
        if show_fact is not None:
            self.curr_fact = show_fact

        if (self.curx + 1) == len(self.new_facts):
            self.user_seen_all = True

        self.refresh_header()
        self.refresh_footer()
        self.refresh_scrollable()

    def refresh_header(self):
        raw_fact = self.raw_facts[self.curx]
        diff = raw_fact.friendly_diff(
            self.curr_fact,
            exclude=set([
                'id',
                'deleted',
                'description',
            ]),
            formatted=True,
        )
        header_parts = self.basic_instructions()
        header_parts += diff
        # <HACK!>
        new_header = to_container(self.assemble_header(header_parts))
        self.hsplit.get_children()[self.header_posit] = new_header

    def basic_instructions(self):
        help_text = '{} {} {}'.format(
            # FIXME: Reuse Carousel for editing saved facts. / And update this text.
            _("Verify all facts being imported."),
            _("Use j/k to go navigate, and e to edit."),
            _("Press Ctrl-s to finish."),
        )
        parts = []
        parts += [('', '\n')]
        parts += [('fg:#5F5FFF bold', help_text)]
        parts += [('', '\n\n')]
        return parts

    def refresh_footer(self):
        def _refresh_footer():
            showing_text = showing_fact()
            helpful_text = helping_text()

            formatted = [
                ('', showing_text),
                # ('', ' / Hints: '),
                ('', ' / '),
                ('', helpful_text),
            ]

            update_footer(formatted)

        def showing_fact():
            if self.curx == -1:
                context = _('stored')
                location = 'ID #{}'.format(self.curr_fact.pk)
            else:
                context = _('new')
                location = '{} of {}'.format(self.curx + 1, len(self.new_facts))
            text = _('Showing {} fact {}').format(context, location)
            return text

        def helping_text():
            key_hints = []
            for keyb in self.key_bonds:
                if keyb.brief is None:
                    continue
                key_hints.append("[{}]: {}".format(keyb.key_hint, keyb.brief))
            text = ' / '.join(key_hints)
            return text

        def update_footer(formatted):
            new_footer = to_container(self.assemble_footer(formatted))
            self.hsplit.get_children()[self.footer_posit] = new_footer

        _refresh_footer()

    def refresh_scrollable(self):
        self.content.buffer.read_only = Never()
        self.content.buffer.text = self.curr_fact.description
        self.content.buffer.read_only = Always()

