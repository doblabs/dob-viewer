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
# (lb): We're using Click only for get_terminal_size. (The
#  UI and user interaction is otherwise all handled by PPT).
import click
from datetime import timedelta

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


# FIXME: Make a crude help. Maybe later make it splashier (different colors, etc.).
#        NOTE: Current multi-line widget does not take inline styling;
#                show what's the proper way to style things?
#              OR: Should we build the Help with widgets for each binding?
CAROUSEL_HELP = _(
""" ┏━━━━━━━━━ NAVIGATION ━━━━━━━━━┳━━━━ EDITING ━━━━┳━━━━━━━ INTERVAL ━━━━━━━━┓
 ┃ → / ←    Next/Previous Fact  ┃  [e] Edit Fact  ┃   Add/Subtract 1 min.   ┃
 ┃ j / k      Same as → / ←     ┠─────────────────╂─────────────────────────┨
 ┃ ↑ / ↓    Move Curson Up/Down ┃    Or edit:     ┃  To Start: Shift → / ←  ┃
 ┃ h / l      Same as ↑ / ↓     ┃  [a]  act@gory  ┃  To End:    Ctrl → / ←  ┃
 ┃ PgUp     Move Cursor Up/Down ┃  [t]  tagslist  ┃  To Both:               ┃
 ┃  PgDn      by pageful        ┃  [d]  descript  ┃       Ctrl-Shift → / ←  ┃
 ┣━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━┻━━━━━┳━━━━━━━━━━━┻━━━━━━━━━┳━━━━━━━━━━━━━━━┫
 ┃  [?] Read   ┃   Ctrl-S  ┃  Ctrl-Q  ┃  [c-p] Split Fact ½ ┃   [u]   Undo  ┃
 ┃  More Help  ┃    Save   ┃   Exit   ┃  [c-e] Emtpy Fact   ┃  [c-r]  Redo  ┃
 ┣━━━━━━━━━━━━━┻━━━━━━━━━━━┻━━━━┳━━━━━┻━━━━━━━━━━━┳━━━━━━━━━┻━━━━━━━━━━━━━━━┫
 ┃ [g-g]    Jump to First Fact  ┃ H A M S T E R   ┃    H A M S T E R        ┃
 ┃  [G]     Jump to Final Fact  ┃  H A M S T E R  ┃     H A M S T E R       ┃
 ┠──────────────────────────────╂─────────────────╂─────────────────────────┨
 ┃ [Home]   First line Descript ┃  H A M S T E R  ┃      H A M S T E R      ┃
 ┃ [End]    Bottom of Descript. ┃   H A M S T E R ┃       H A M S T E R     ┃
 ┣━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━┻━━━━━┯━━━━━━━━━┯━┻━━━━━━━┳━━━━━━━━━━━━━━━━━┫
 ┃  [?] Close  ┃  [q] Easy  ┃  [c-c]  │  [c-x]  │  [c-v]  ┃   [c-z]  Undo   ┃
 ┃  this Help  ┃    Exit    ┃   Copy  │   Cut   │  Paste  ┃   [c-y]  Redo   ┃
 ┗━━━━━━━━━━━━━┻━━━━━━━━━━━━┻━━━━━━━━━┷━━━━━━━━━┷━━━━━━━━━┻━━━━━━━━━━━━━━━━━┛

    """.rstrip()
)


NUM_HELP_PAGES = 2


class FactsCarousel(object):
    """"""
    def __init__(
        self,
        controller,
        old_fact,
        new_facts,
        raw_facts,
        backup_callback,
        dry,
    ):
        self.controller = controller
        self.old_facts = [old_fact, ] if old_fact is not None else []
        self.old_edits = {}
        self.new_facts = new_facts
        self.raw_facts = raw_facts
        self.backup_callback = backup_callback
        self.dry = dry

        self.curx = 0
        self.user_seen_all = False

        # FIXME: (lb): Make height configurable/adjustable.
        self.scrollable_height = 10

        self.showing_help = 0

        self.setup_async()

    def setup_async(self):
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
        #
        # Argh. I'm getting a stack trace after importing and saving 100s of
        # facts. Doesn't happen on smaller test file, just a really big actual
        # factual live import file I have...
        #
        #  Exception ignored in: <bound method BaseEventLoop.__del__
        #       of <_UnixSelectorEventLoop running=False closed=True debug=False>>
        #  Traceback (most recent call last):
        #    File "/usr/lib/python3.5/asyncio/base_events.py", line 431, in __del__
        #    File "/usr/lib/python3.5/asyncio/unix_events.py", line 58, in close
        #    File "/usr/lib/python3.5/asyncio/unix_events.py", line 139,
        #           in remove_signal_handler
        #    File "/usr/lib/python3.5/signal.py", line 47, in signal
        #  TypeError: signal handler must be signal.SIG_IGN, signal.SIG_DFL,
        #    or a callable object
        #
        # I looked at the PPT docs but didn't glean much.
        #
        #   https://python-prompt-toolkit.readthedocs.io/
        #     en/2.0/pages/advanced_topics/asyncio.html
        #
        # And I'm not really versed in asyncio... so, well, disable this.
        self.async_enable = False

    def gallop(self):
        self.stand_up()
        if self.async_enable:
            # Tell prompt_toolkit to use asyncio.
            use_asyncio_event_loop()
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
        if self.old_facts and not self.old_edits:
            # Editing(/Viewing) old Facts, and none were edited.
            return True
        question = _('\nReally exit without saving?')
        confirmed = confirm(question, erase_when_done=True)
        if self.old_facts:
            del self.new_facts[:]
            del self.raw_facts[:]
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
        edit_fact = self.editable_fact()
        used_prompt = self.prompt_user(edit_fact, used_prompt)
        self.recompose_new_facts(edit_fact)
        self.backup_callback()
        self.refresh_fact()
        return used_prompt

    def editable_fact(self):
        if not self.old_facts:
            # This is an import job, so curr_fact is already new.
            edit_fact = self.curr_fact
        else:
            # This is an edit-existing command, and we only want to
            # keep track of Facts that the user actually edits, and
            # is not just viewing. Here we make a Fact copy on demand
            # for the user to edit, if we haven't made one already.
            try:
                edit_fact = self.old_edits[self.curr_fact.pk]
            except KeyError:
                edit_fact = self.curr_fact.copy()
        return edit_fact

    def prompt_user(self, edit_fact, used_prompt):
        used_prompt = ask_user_for_edits(
            self.controller,
            edit_fact,
            always_ask=True,
            prompt_agent=used_prompt,
            restrict_edit=self.restrict_edit,
        )
        return used_prompt

    def recompose_new_facts(self, edit_fact):
        if not self.old_facts:
            return
        if edit_fact != self.curr_fact:
            self.old_edits[self.curr_fact.pk] = edit_fact
        else:
            try:
                del self.old_edits[self.curr_fact.pk]
            except KeyError:
                pass
        del self.new_facts[:]
        for pk in sorted(self.old_edits.keys()):
            self.new_facts.append(self.old_edits[pk])

    def stand_up(self):
        self.prepare_first_fact()
        self.setup_scrollable()
        self.assemble_application()
        self.refresh_fact()

    def prepare_first_fact(self):
        self.new_i = None
        if self.old_facts:
            assert len(self.old_facts) == 1
            assert self.old_facts[0].pk > 0
            self.curx = -1
            self.curr_fact = self.old_facts[0]
            self.new_i = 0
        elif len(self.new_facts) > 0:
            self.curx = 0
            self.curr_fact = self.new_facts[self.curx]
        else:
            self.curx = -1
            self.curr_fact = self.controller.antecedent()
            if self.curr_fact is not None:
                self.old_facts.append(self.curr_fact)
                self.new_i = 0

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
        # FIXME: (lb): These hardcoded colors are "temporary",
        #        until we (I?) implement color schemes.
        style = Style([
            ('header-label', 'bg:#888800 #000000'),
            ('content-area', 'bg:#00aa00 #000000'),
            # ('content-help', 'bg:#0000aa #000000'),
            ('content-help', 'bg:#226666 #000000'),
        ])
        return style

    def setup_key_bindings(self):
        return self.setup_key_bindings_view_only()

    def setup_key_bindings_view_only(self):
        key_bindings = KeyBindings()

        # The order here is the order used in the footer help.
        self.key_bonds = [
            KeyBond('?', brief=_('help'), action=self.rotate_help),
            #
            KeyBond('j', brief=_('prev'), action=self.scroll_left),
            KeyBond('k', brief=_('next'), action=self.scroll_right),
            KeyBond(Keys.Left, brief=None, action=self.scroll_left),
            KeyBond(Keys.Right, brief=None, action=self.scroll_right),
            #
            KeyBond('G', brief=None, action=self.scroll_fact_last),
            KeyBond(('g', 'g'), brief=None, action=self.scroll_fact_first),
            #
            KeyBond('h', brief=None, action=self.cursor_up_one),
            KeyBond('l', brief=None, action=self.cursor_down_one),
            #
            KeyBond('e', brief=None, action=self.edit_fact),
            KeyBond('a', brief=_('act@'), action=self.edit_actegory),
            KeyBond('d', brief=_('desc'), action=self.edit_description),
            KeyBond('t', brief=_('#tag'), action=self.edit_tags),
            #
            KeyBond('c-s', brief=_('save'), action=self.finish_command),
            KeyBond('c-q', brief=_('quit'), action=self.cancel_command),
            KeyBond('q', None, action=self.cancel_softly),
            #
            KeyBond('pageup', brief=None, action=self.scroll_up),
            KeyBond('pagedown', brief=None, action=self.scroll_down),
            KeyBond('home', brief=None, action=self.scroll_top),
            KeyBond('end', brief=None, action=self.scroll_bottom),
            #
            KeyBond('s-left', brief=None, action=self.edit_time_decrement_start),
            KeyBond('s-right', brief=None, action=self.edit_time_increment_start),
            KeyBond('c-left', brief=None, action=self.edit_time_decrement_end),
            KeyBond('c-right', brief=None, action=self.edit_time_increment_end),
            KeyBond('c-s-left', brief=None, action=self.edit_time_decrement_both),
            KeyBond('c-s-right', brief=None, action=self.edit_time_increment_both),
            #
            # Vim maps Ctrl-z and Ctrl-y for undo and redo;
            # and u/U to undo count/all and Ctrl-R to redo (count).
            KeyBond('c-z', brief=None, action=self.undo_command),
            KeyBond('c-y', brief=None, action=self.redo_command),
            # (lb): Too many options!
            # MAYBE: Really mimic all of Vi's undo/redo mappings,
            #        or just pick one each and call it good?
            KeyBond('u', brief=None, action=self.undo_command),
            KeyBond('c-r', brief=None, action=self.redo_command),
            # (lb): Oh so many duplicate redundant options!
            KeyBond('r', brief=None, action=self.redo_command),
            #
            # (lb): 2018-06-28: Remaining are WIP. And I'm undecided on
            #       bindings. Maybe Alt-key bindings for Split & Clear?
            #       I like c-w and c-e because they're adjacent keys.
            #       Or m-w and m-e could also work, and then Ctrl-W is
            #       not confused with typical "close" command (whatever
            #       that would mean in Carousel context).
            # FIXME/2018-06-28: (lb): I'll clean this up. Eventually.
            #
            # KeyBond('c-p', brief=None, action=self.fact_split),
            # KeyBond('c-w', brief=None, action=self.fact_split),
            # KeyBond('c-t', brief=None, action=self.fact_split),
            #
            # KeyBond('c-e', brief=None, action=self.fact_wipe),
            # KeyBond('m-w', brief=None, action=self.fact_wipe),
            # KeyBond('c-a', brief=None, action=self.fact_wipe),
            KeyBond('m-p', brief=None, action=self.fact_split),
            KeyBond('m-e', brief=None, action=self.fact_wipe),
            #
            KeyBond('c-c', brief=None, action=self.fact_copy),
            KeyBond('c-x', brief=None, action=self.fact_cut),
            KeyBond('c-v', brief=None, action=self.fact_paste),
        ]

        for keyb in self.key_bonds:
            if isinstance(keyb.keycode, tuple):
                key_bindings.add(*keyb.keycode)(keyb.action)
            else:
                key_bindings.add(keyb.keycode)(keyb.action)

        return key_bindings

    def build_application_object(self):
        # (lb): By default, the app uses editing_mode=EditingMode.EMACS,
        # which adds a few key bindings. One binding in particular is a
        # little annoying -- ('c-x', 'c-x') -- because PPT has to wait
        # for a second key press, or a timeout, to resolve the binding.
        # E.g., if you press 'c-x', it takes a sec. until our handler is
        # called (or, it's called if you press another key, but then the
        # response seems weird, i.e., 2 key presses are handle seemingly
        # simultaneously after the second keypress, rather than being
        # handled individually as the user presses them keys). In any
        # case -- long comment! -- set editing_mode to something other
        # than EditingMode.EMACS or EditingMode.VI (both are just strings).

        application = Application(
            layout=self.layout,
            key_bindings=self.key_bindings,
            full_screen=False,
            erase_when_done=True,
            # Enables mouse wheel scrolling.
            # CAVEAT: Steals from terminal app!
            #   E.g., while app is active, mouse wheel scrolling no
            #   longer scrolls the desktop Terminal app window, ha!
            # FIXME: Make this feature optionable. Seems like some
            #   people may appreciate this wiring.
            mouse_support=True,
            style=self.style,
            editing_mode='',  # Disable build-in buffer editing bindings.
        )
        return application

    def runloop(self):
        self.confirm_exit = False
        self.enduring_edit = False
        self.restrict_edit = ''
        if self.async_enable:
            # Run application async.
            asyncio.get_event_loop().run_until_complete(
                self.application.run_async().to_asyncio_future(),
            )
        else:
            self.application.run()

    # ***

    def rotate_help(self, event):
        assert NUM_HELP_PAGES == 2  # Otherwise, we need to update this logic:
        self.showing_help = (self.showing_help + 1) % (NUM_HELP_PAGES + 1)
        if self.showing_help == 1:
            self.scroll_top(event)
        elif self.showing_help == 2:
            self.scroll_bottom(event)
        else:
            self.scroll_top(event)
        self.refresh_fact()

    class Decorators(object):
        @classmethod
        def reset_showing_help(decorators, func):
            def _wrapper(self, event, *args, **kwargs):
                # This won't redraw because we don't call refresh_scrollable.
                # So, if, e.g., user is on first Fact and clicks Left, the
                # Help will not go away, because decrement() won't refresh.
                self.showing_help = 0
                func(self, event, *args, **kwargs)
            return _wrapper

    # ***

    @Decorators.reset_showing_help
    def cancel_command(self, event):
        """"""
        self.confirm_exit = True
        event.app.exit()

    @Decorators.reset_showing_help
    def cancel_softly(self, event):
        """"""
        if self.old_facts and not self.old_edits:
            self.confirm_exit = True
            event.app.exit()

    @Decorators.reset_showing_help
    def finish_command(self, event):
        """"""
        event.app.exit()

    # ***

    @Decorators.reset_showing_help
    def undo_command(self, event):
        """"""
        pass  # FIXME: Implement

    @Decorators.reset_showing_help
    def redo_command(self, event):
        """"""
        pass  # FIXME: Implement

    # ***

    @Decorators.reset_showing_help
    def fact_split(self, event):
        """"""
        pass  # FIXME: Implement

    @Decorators.reset_showing_help
    def fact_wipe(self, event):
        """"""
        pass  # FIXME: Implement

    @Decorators.reset_showing_help
    def fact_copy(self, event):
        """"""
        pass  # FIXME: Implement

    @Decorators.reset_showing_help
    def fact_cut(self, event):
        """"""
        pass  # FIXME: Implement

    @Decorators.reset_showing_help
    def fact_paste(self, event):
        """"""
        pass  # FIXME: Implement

    # ***

    # FIXME: (lb): These time +/- bindings are pretty cool,
    #        but they should and/or create conflicts,
    #        or affect the time of adjacent facts...
    #        so you may need to show times of adjacent facts,
    #        and/or you could auto-adjust adjacent facts' times,
    #        perhaps not letting user decrement below time of fact
    #        before it, or increment above time of fact after it.
    #        (at least need to preload the before and after facts for
    #        the current fact).
    #        for now, you can raw-edit factoid to change type
    #        and resolve conflicts. or you could edit facts in
    #        carousel and resolve conflicts yourself, before saving.
    #
    #        maybe if you begin to edit time, then you show
    #        adjacent fact's (or facts') time(s).
    #
    #        I think easiest option is to just adjust adjacent
    #        facts' times -- without showing them -- and to
    #        stop at boundary, i.e., when adjacent fact would
    #        be at 0 time (albeit, when if seconds don't match?
    #        you should normalize and remove seconds when you
    #        you adjust time!)
    #    1.  - normalize to 0 seconds on adjust
    #    2.  - change adjacent facts' time(s), too
    #    3.  - stop at adjacent fact boundary
    #    4.  - option to delete fact -- so user could either change to
    #          adjacent fact and edit its time to make more room for
    #          fact being re-timed; or user could switch to adjacent
    #          fact and delete it, poof!
    #    5.  - undo/redo stack of edit_facts
    #          e.g., undo delete fact command, or undo any edit:
    #             act@cat, tags, description!
    #             keep a copy of undo fact in carousel
    #    6.  - insert new fact -- or split fact! split fact in twain...
    #          YES! you could even have a split fact command, and then
    #          a clear fact command ... (s)plit fact... (C)lear fact...
    #          or maybe (S) and (C) ... this makes the redo/undo trickier...
    #          perhaps each redo/undo state is a copy of edit_facts?
    #          i think the trickier part is coordinating new_facts
    #          and edit_facts -- the lookup can return multiple facts,
    #          i'm guessing... and then the new split facts will just
    #          show the diff each against the same base fact... and on
    #          save... what? they all have the same split_from, I guess...
    #          because we don't really use split_from yet... OK, this is
    #          doable, super doable... and it could make my fact entering
    #          at end of day easier? or fact cleanup, i should mean, e.g.,
    #          if I had a fact that was 6 hours long, I could split it
    #          in two, and then adjust the time quickly with arrow keys!
    #    7.  - (h)elp option? TOGGLE HELP IN DESCRIPTION BOX!! You could
    #          probably easily redraw the header, too, to not show a fact...
    #          maybe use Header and Description area -- can I use a new
    #          Layout item or whatever from PPT and swap out current
    #          display? OR, leave the Fact header, because user might
    #          want to use one of the HELP KEYS while VIEWING THE HELP.
    #          So show help, and on any command, clear the help!
    #          And does this mean I should add more meta to the key bindings
    #          and build the help automatically? Or should I, say, just
    #          make a custom string and maintain the help separately?
    #          the latter is probably easiest...
    #          - Use different background color when displaying the help!
    #
    #        - user can use left/right to see adjacent facts, like normal
    #          (i.e., do not add more widgets/info to carousel!)
    #        - user can adjust adjacent facts' times as well, to
    #          keep pushing facts' times around
    #
    #    X.  - swap 2 adjacent Facts? seems like it makes sense,
    #          but also seems useless, as in, what use case would
    #          have user wanting to swap 2 facts?? i've never wanted
    #          to do that.

    def edit_time_decrement_start(self, event):
        self.edit_time_adjust(timedelta(minutes=-1), 'start')

    def edit_time_increment_start(self, event):
        self.edit_time_adjust(timedelta(minutes=1), 'start')

    def edit_time_decrement_end(self, event):
        self.edit_time_adjust(timedelta(minutes=-1), 'end')

    def edit_time_increment_end(self, event):
        self.edit_time_adjust(timedelta(minutes=1), 'end')

    def edit_time_decrement_both(self, event):
        self.edit_time_adjust(timedelta(minutes=-1), 'start', 'end')

    def edit_time_increment_both(self, event):
        self.edit_time_adjust(timedelta(minutes=1), 'start', 'end')

    def edit_time_adjust(self, delta_mins, *attrs):
        edit_fact = self.editable_fact()
        for start_or_end in attrs:
            curr_time = getattr(edit_fact, start_or_end)
            setattr(edit_fact, start_or_end, curr_time + delta_mins)
        self.recompose_new_facts(edit_fact)
        self.backup_callback()
        self.refresh_fact()

    # ***

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

    # ***

    def cursor_up_one(self, event):
        """"""
        self.content.buffer.cursor_up(1)

    def cursor_down_one(self, event):
        """"""
        self.content.buffer.cursor_down(1)

    def scroll_down(self, event):
        """"""
        view_height = self.scrollable_height - 1
        if self.content.buffer.document.cursor_position_row == 0:
            # If cursor is at home posit, first page down moves cursor
            # to bottom of view. So scroll additional page, otherwise
            # user would have to press PageDown twice to see more text.
            view_height *= 2
        self.content.buffer.cursor_down(view_height)
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

    def scroll_top(self, event):
        """"""
        self.content.buffer.cursor_position = 0

    def scroll_bottom(self, event):
        """"""
        self.content.buffer.cursor_position = len(self.content.buffer.text)
        self.reset_cursor_left_column()

    # ***

    @Decorators.reset_showing_help
    def scroll_left(self, event):
        """"""
        self.decrement()
        self.reset_cursor_left_column()

    @Decorators.reset_showing_help
    def scroll_right(self, event):
        """"""
        self.increment()
        self.reset_cursor_left_column()

    def decrement(self):
        """"""
        prev_fact = None
        if self.curx >= 0:
            if self.curx > 0:
                self.curx -= 1
                prev_fact = self.new_facts[self.curx]
        else:
            assert self.curx == -1
            if self.new_i == 0:
                prev_fact = self.controller.facts.antecedent(self.curr_fact)
                if prev_fact is not None:
                    self.old_facts.insert(0, prev_fact)
            else:
                self.new_i -= 1
                prev_fact = self.old_facts[self.new_i]
        if prev_fact is None:
            return
        self.refresh_fact(prev_fact)

    def increment(self):
        """"""
        next_fact = None
        if self.curx >= 0:
            if (self.curx + 1) < len(self.new_facts):
                self.curx += 1
                next_fact = self.new_facts[self.curx]
        else:
            assert self.curx == -1
            if (self.new_i + 1) < len(self.old_facts):
                self.new_i += 1
                next_fact = self.old_facts[self.new_i]
            else:
                next_fact = self.controller.facts.subsequent(self.curr_fact)
                if next_fact is not None:
                    self.old_facts.append(next_fact)
                    self.new_i += 1
                    assert self.new_i == (len(self.old_facts) - 1)
        if next_fact is None:
            return
        self.refresh_fact(next_fact)

    @Decorators.reset_showing_help
    def scroll_fact_first(self, event):
        """"""
        pass  # FIXME: Implement

    @Decorators.reset_showing_help
    def scroll_fact_last(self, event):
        """"""
        pass  # FIXME: Implement

    # ***

    def refresh_fact(self, show_fact=None):
        """"""
        if show_fact is not None:
            self.curr_fact = show_fact

        if self.curx == -1 or (self.curx + 1) == len(self.new_facts):
            # Means user navigated right through all Facts and "saw" everything.
            # (lb): Not sure how useful this really is....
            self.user_seen_all = True

        self.refresh_header()
        self.refresh_footer()
        self.refresh_scrollable()

    def refresh_header(self):
        raw_fact, curr_fact = self.which_facts()
        diff = raw_fact.friendly_diff(
            curr_fact,
            exclude=set([
                'id',
                'deleted',
                'description',
            ]),
            formatted=True,
            show_elapsed=True,
        )
        header_parts = self.basic_instructions()
        header_parts += diff
        # <HACK!>
        new_header = to_container(self.assemble_header(header_parts))
        self.hsplit.get_children()[self.header_posit] = new_header

    def which_facts(self):
        if not self.old_facts:
            raw_fact = self.raw_facts[self.curx]
            curr_fact = self.curr_fact
        else:
            raw_fact = self.curr_fact
            try:
                curr_fact = self.old_edits[self.curr_fact.pk]
            except KeyError:
                curr_fact = self.curr_fact
        return raw_fact, curr_fact

    def basic_instructions(self):
        # (lb): This if-else is so procedural and hardcoded. Oh well.
        if not self.old_facts:
            instruct = _("Verify facts being imported.")
        else:
            instruct = _("Browse and edit facts.")
        help_text = '{} {}'.format(
            instruct,
            _("Press '?' for complete help. Ctrl-S to save, or Ctrl-C to quit."),
        )
        parts = []
        parts += [('', '\n')]
        parts += [('fg:#5F5FFF bold', help_text)]
        parts += [('', '\n\n')]
        return parts

    def refresh_footer(self):
        """"""
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
                context = _('Old')
                location = 'ID #{}'.format(self.curr_fact.pk)
            else:
                context = _('New')
                location = '{:>{}} of {}'.format(
                    self.curx + 1,
                    len(str(len(self.new_facts))),
                    len(self.new_facts),
                )
            text = _('{} Fact {}').format(context, location)
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
        if self.showing_help:
            # MAYBE: (lb): It is easy to format a PPT Frame's content?
            #   (I tried passing HTML(CAROUSEL_HELP) but, uh, nope.)
            #   (This is not too important; I thought it might be nice
            #   (polishing feature) to beautify the help (even more).)
            content = CAROUSEL_HELP
            self.scrollable.container.style = 'class:content-help'
        else:
            _raw_fact, curr_fact = self.which_facts()
            content = curr_fact.description or ''
            self.scrollable.container.style = 'class:content-area'
        self.content.buffer.read_only = Never()
        self.content.buffer.text = content
        self.content.buffer.read_only = Always()

