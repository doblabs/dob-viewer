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

import json

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

    # *** interface_keys.Key_Bonder.widget_focus()

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

    # *** interface_keys.Key_Bonder.save_and_quit()

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
        # There are two Quit mapping: Ctrl-Q and ESCAPE.
        # - NOTE: Using 'escape' to exit is slow because PPT waits to
        #         see if escape sequence follows (which it wouldn't, after
        #         an 'escape', but meta-combinations start with an escape).
        #           tl;dr: 'escape' to exit is slow b/c alias resolution.
        # - NOTE: BUGBUG: Without the Ctrl-Q binding, if the user presses
        #         Ctrl-Q in the app., if becomes unresponsive.
        #         2020-04-11: I have not investigated, just noting it now
        #         that we're opening up keybindings for user to screw up! =)
        return json.dumps([('c-q',), ('escape',)])

    # *** interface_keys.Key_Bonder.edit_time()

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def editable_text_enter(self):
        return 'enter'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def toggle_focus_description(self):
        return 'd'

    # *** interface_keys.Key_Bonder.undo_redo()

    # Vim maps Ctrl-z and Ctrl-y for undo and redo;
    # and u/U to undo count/all and Ctrl-R to redo (count).
    #
    # (lb): So many undo/redo options!
    # MAYBE: Really mimic all of Vi's undo/redo mappings,
    #        or just pick one each and call it good?
    # - Or let user decide! 2020-04-11: Now it's customizable.

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def undo_command(self):
        return json.dumps([('c-z',), ('u',)])

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def redo_command(self):
        return json.dumps([('c-y',), ('c-r',), ('r',)])

    # *** interface_keys.Key_Bonder.normal()

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def rotate_help(self):
        return '?'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def dev_breakpoint(self):
        # I.e., 'm-=', aka, <Alt+=>.
        return json.dumps([('escape', '=')])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def jump_fact_dec(self):
        # I.e., 'j', and PTK's Keys.Left.
        return json.dumps([('j',), ('left',)])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def jump_fact_inc(self):
        # I.e., 'k', and PTK's Keys.Right.
        return json.dumps([('k',), ('right',)])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def jump_day_dec(self):
        return json.dumps([
            ('J',),
            # This only wired to Escape then Arrow, not Meta-Arrow.
            ('escape', 'left'),
        ])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def jump_day_inc(self):
        return json.dumps([
            ('K',),
            # This only wired to Escape then Arrow, not Meta-Arrow.
            ('escape', 'right'),
        ])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def jump_rift_dec(self):
        return json.dumps([('g', 'g')])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def jump_rift_inc(self):
        return 'G'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def cursor_up_one(self):
        return 'h'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def cursor_down_one(self):
        return 'l'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def ignore_key_press_noop(self):
        return json.dumps([
            # NOTE: If you want to see how key presses map to KeyPresses, try:
            #         $ cd path/to/python-prompt-toolkit/tools
            #         $ python3 debug_vt100_input.py
            #         # PRESS ANY KEY
            # Catch Alt-Up, etc., explicitly -- though we don't do anything with it --
            # so that the 'escape'-looking prefix does not trigger bare 'escape' handler.
            # ((lb): There might be a different way to do this... not sure.)
            ('escape', '[', '1', ';', '4', 'A'),  # Alt-UP
            ('escape', '[', '1', ';', '4', 'B'),  # Alt-DOWN
            ('escape', '[', '1', ';', '4', 'C'),  # Alt-RIGHT [bunch of snowflakes]
            ('escape', '[', '1', ';', '4', 'D'),  # Alt-LEFT
        ])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def scroll_up(self):
        return 'pageup'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def scroll_down(self):
        return 'pagedown'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def scroll_top(self):
        return 'home'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def scroll_bottom(self):
        return 'end'

    # *** interface_keys.Key_Bonder.edit_fact()

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_fact(self):
        # Raw Fact Editing. With a Capital E.
        return 'E'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_description(self):
        return 'd'

    # ***

    # Edit act@gory and tags using prompt__awesome.
    # (lb): This is pretty cool. prompt_awesome was built first,
    # and then I got comfortable with PPT and built the Carousel,
    # and then I was able to stick one inside the other, and it's
    # just awesome awesome now.

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_actegory(self):
        return 'a'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_tags(self):
        return 't'

    # *** interface_keys.Key_Bonder.nudge_time_with_arrows()

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_time_decrement_start(self):
        return 's-left'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_time_increment_start(self):
        return 's-right'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_time_decrement_end(self):
        return 'c-left'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_time_increment_end(self):
        return 'c-right'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_time_decrement_both(self):
        # FIXME/2019-01-21: Can you check if running in Terminator
        #  and warn-tell user. And/Or: Customize Key Binding feature.
        # In Terminator: Shift+Ctrl+Left/+Right: Resize the terminal left/right.
        #  (lb): I've disabled the 2 bindings in Terminator,
        #   so this works for me... so fixing it is a low priority!
        return 's-c-left'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_time_increment_both(self):
        # See previous comment about 's-c-left': The user's terminal probably
        # possibly has a mapping already that shadows this. (They can disable
        # their terminal mappings, though, for it to pass through.)
        return 's-c-right'

    # *** interface_keys.Key_Bonder.create_delete_fact()

    # FIXME/2020-04-11: Not implemented.
    if False:

        @property
        @ConfigRoot.setting(
            _("XXX"),
        )
        def fact_split(self):
            return json.dumps([('escape', 'p')])

        # ***

        @property
        @ConfigRoot.setting(
            _("XXX"),
        )
        def fact_erase(self):
            return json.dumps([('escape', 'e')])

        # ***

        @property
        @ConfigRoot.setting(
            _("XXX"),
        )
        def fact_merge_prev(self):
            return json.dumps([('escape', 'm', 'left')])

        # ***

        @property
        @ConfigRoot.setting(
            _("XXX"),
        )
        def fact_merge_next(self):
            return json.dumps([('escape', 'm', 'right')])

    # *** interface_keys.Key_Bonder.clipboard()

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def fact_copy_fact(self):
        return 'c-c'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def fact_cut(self):
        return 'c-x'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def fact_paste(self):
        return 'c-v'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def fact_copy_activity(self):
        return json.dumps([('A', 'c-c')])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def fact_copy_tags(self):
        return json.dumps([('T', 'c-c')])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def fact_copy_description(self):
        return json.dumps([('D', 'c-c')])

