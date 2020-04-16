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
    'json_load_keycodes',
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
        # (lb): I had this mapped to Ctrl-W, but that feels like it should
        # just close the application... which would be a simple exit.
        # - I think Ctrl-W would break people's mental model:
        #     return 'c-w'
        # - But users can perform this same (two-commands-in-one) feature via
        #   the `:wq` commando. Except the commando has option to linger after
        #   save, to display the 'Saved {} Facts' message before exiting.
        # - Here we return the empty string to disable it, but it's left as a
        #   configurable option should the user want to map it to use it.
        return ''

    # ***

    @property
    @ConfigRoot.setting(
        _("Exit Quietly if No Changes"),
    )
    def exit_quietly(self):
        return 'q'

    # ***

    @property
    @ConfigRoot.setting(
        _("Exit with Prompt if Changes"),
    )
    def exit_command(self):
        # There are two Quit mapping: Ctrl-Q and ESCAPE.
        # - NOTE: Using 'escape' to exit is slow because PPT waits to
        #         see if escape sequence follows (which it wouldn't, after
        #         an 'escape', but meta-combinations start with an escape).
        #           tl;dr: 'escape' to exit is slow b/c alias resolution.
        # - NOTE: BUGBUG: Without the Ctrl-Q binding, if the user presses
        #         Ctrl-Q in the app., if becomes unresponsive.
        #         2020-04-11: I have not investigated, just noting it now
        #         that we're opening up keybindings for user to screw up! =)
        return 'c-q'

    # *** interface_keys.Key_Bonder.edit_time()

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_time_enter(self):
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
        # I.e., 'j', or left arrow.
        return json.dumps([('j',), ('left',)])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def jump_fact_inc(self):
        # I.e., 'k', or right arrow.
        return json.dumps([('k',), ('right',)])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def jump_day_dec(self):
        # I.e., 'J', or Alt-left arrow.
        return json.dumps([('J',), ('escape', 'left')])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def jump_day_inc(self):
        # I.e., 'J', or Alt-right arrow.
        return json.dumps([('K',), ('escape', 'right')])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def jump_rift_dec(self):
        # A good pneumonic: 'F'irst Fact.
        return 'F'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def jump_rift_inc(self):
        # A good pneumonic: 'f'inal Fact.
        return 'f'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def jump_fact_first(self):
        return json.dumps([('g', 'g')])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def jump_fact_final(self):
        return 'G'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def cursor_up_one(self):
        return json.dumps([('h',), ('up',)])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def cursor_down_one(self):
        return json.dumps([('l',), ('down',)])

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
        # Edit merry-go-round: Prompt for act@gory, then tags, then description.
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

    # *** interface_keys.Key_Bonder.nudge_time()

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_time_decrement_start(self):
        return json.dumps([('s-left',), (',',)])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_time_increment_start(self):
        return json.dumps([('s-right',), ('.',)])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_time_decrement_end(self):
        return json.dumps([('c-left',), ('[',)])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_time_increment_end(self):
        return json.dumps([('c-right',), (']',)])

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

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_time_decrement_start_5min(self):
        return '<'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_time_increment_start_5min(self):
        return '>'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_time_decrement_end_5min(self):
        return '{'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def edit_time_increment_end_5min(self):
        return '}'

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

    # *** interface_keys.Key_Bonder.vim_like_command*()

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def begin_commando(self):
        return ':'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def final_commando(self):
        return 'enter'

    # *** The ':' command strings.

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    # Should this be 'save_commando' for consistency with Ctrl-S command,
    # or should this be named with 'write' because 'w' and Vim suggest that?
    def write_commando(self):
        # As in, `:w`.
        return 'w'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def quit_commando(self):
        # As in, `:q`.
        return 'q'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def save_quit_commando(self):
        # As in, `:wq`.
        return 'wq'

    # *** interface_keys.Key_Bonder.delta_time_width()

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def begin_delta_time_start(self):
        return '+'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def begin_delta_time_end(self):
        return '-'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def allow_time_gap(self):
        return '!'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def final_delta_time_apply(self):
        return json.dumps([('enter',), ('tab',)])

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def final_delta_time_minutes(self):
        return 'm'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def final_delta_time_hours(self):
        return 'h'

    # ***

    # Reminder from nark's parse_time: iso8601 date formats:
    #   YYYY-MM-DD | YYYYMMDD | YYYY-MM | YYYY
    # Note that the only non-digit character allowed is the dash/minus.
    # - Here we allow the user to specify other characters that are okay
    #   to use as a separator, so we're not limiting to just dash.
    # - Note, too, that we can allow YYYYMM (sans dash) because why not.

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def date_separators(self):
        # NOTE: These are used in a regex, so escape as necessary.
        return json.dumps([
            # Conventional `YYYY-MM/DD` separators.
            ('-',), ('/',),
            # Convention separators between `YYYYMMDD` and `hh:mm`.
            (' ',), ('t',), ('T',),
            # Conventional `hh:mm` separator.
            (':',),
        ])

    # ***

    # Command shortcuts.

    # 2020-04-15: (lb): I did not consider much before picking the
    # key bindings below. There are not any obvious mappings, other
    # than perhaps (a) avoiding keys that have universal mappings
    # (like Ctrl-c, Ctrl-q, etc.). Also (b) making it easy to press
    # (i.e., not Ctrl-g), as these may be used often.
    # - I suppose between 'c-e' and 'V', on an English keyboard, they
    #   are similar motions (pinky plus pointer), so maybe that'll
    #   help people remember. And 'o' is pretty baked in from Vim.
    #   Open a new fact -- and prompt for the act@gory.

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def copy_complete_and_paste_active(self):
        return 'c-e'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def copy_complete_and_paste_new(self):
        return 'V'

    # ***

    @property
    @ConfigRoot.setting(
        _("XXX"),
    )
    def complete_and_prompt_new(self):
        # 'a' for act@gory, like plain 'a' command mapping.
        # Or not. 'c-a' is a common tmux prefix key.
        #  return 'c-a'
        # How 'bout, 'o'pen a new entry?
        return 'o'

    # ***


# ***

def json_load_sublisted(cfgname, cfgval):
    def _json_load_sublisted():
        # (lb): We could skip the startswith check and just use except,
        #       but it feels more readable this way.
        if not cfgval.startswith('['):
            # Just a string. Except don't bother with the empty string,
            # which is used to disable a key command mapping.
            if cfgval:
                return [cfgval], None
            return [], None
        try:
            # List of lists: Top-level is list, and elements are lists.
            # - This is currently used for keybindings, which can either
            #   be a single element sublist (representing a single key),
            #   or the sublist could be a key binding tuple (well, it's
            #   json, so a list), which represents a multiple-key binding.
            keycodes = json.loads(cfgval)
            assert isinstance(keycodes, list)  # Would it be anything else?
            if not sanity_check(keycodes):
                return None, error_not_list_within_lists()
        except json.decoder.JSONDecodeError as err:
            return None, error_not_list_within_lists(err)
        return keycodes, None

    def sanity_check(keycodes):
        return all(isinstance(keycode, list) for keycode in keycodes)

    def error_not_list_within_lists(err=''):
        append_err = ' (“{}”)'.format(err) if err else ''
        return (_(
            'ERROR: Key binding for ‘{}’ should be single key'
            ' or list of lists, not: {}{}'
            .format(cfgname, cfgval, append_err)
        ))

    return _json_load_sublisted()


# ***

@ConfigRoot.section('custom-paste')
class DobViewerCustomPaste(object):
    """"""

    def __init__(self, *args, **kwargs):
        pass

    # ***

    # (lb): This is the best I've got on a moment's thought:
    # Create placeholder config so that it'll be read from user's dob.conf.
    # (lb): This is not the cleanest solutions (we have to arbitrarily decide how
    # many placeholders to create), but it's otherwise transparent to the user.

    def add_custom_paste(postfix):
        """"""
        factoid_name = 'factoid_{}'.format(postfix)
        mapping_name = 'mapping_{}'.format(postfix)

        @property
        @ConfigRoot.setting(
            _("XXX"),
            name=factoid_name,
            hidden=True,
        )
        def factoid_prop(self):
            return ''

        @property
        @ConfigRoot.setting(
            _("XXX"),
            name=mapping_name,
            hidden=True,
        )
        def mapping_prop(self):
            return ''

    A_PERFECT_NUMBER = 28

    for postfix in range(1, A_PERFECT_NUMBER):
        add_custom_paste(postfix)

