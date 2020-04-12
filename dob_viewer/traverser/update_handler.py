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

"""Facts Carousel"""

import re
import time
from datetime import timedelta

from gettext import gettext as _

from .exceptions import catch_action_exception
from .zone_content import ZoneContent

__all__ = (
    'UpdateHandler',
)


class UpdateHandler(object):
    """"""
    def __init__(self, carousel):
        self.carousel = carousel

        self.last_time_time_adjust = None
        self.press_cnt_time_adjust = 0

    # ***

    def standup(self):
        self.edits_manager = self.carousel.edits_manager
        self.zone_manager = self.carousel.zone_manager

    # ***

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def undo_command(self, event):
        """"""
        undone = self.edits_manager.undo_last_edit()
        if not undone:
            hot_notif = _("Already at oldest change")  # Like Vim says!
        else:
            self.zone_manager.rebuild_viewable()
            # FIXME: Do not exceed terminal width.
            #  hot_notif = _("Restored: {0}").format(edited_fact.short)
            hot_notif = _("Undid last change. Press Ctrl-y to redo")
        self.zone_manager.update_status(hot_notif)

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def redo_command(self, event):
        """"""
        redone = self.edits_manager.redo_last_undo()
        if not redone:
            hot_notif = _("Already at newest change")  # Same says Vim.
        else:
            self.zone_manager.rebuild_viewable()
            # FIXME: Do not exceed terminal width.
            #  hot_notif = _("Restored: {0}").format(edited_fact.short)
            hot_notif = _("Redid last change. Press Ctrl-z to undo")
        self.zone_manager.update_status(hot_notif)

    # ***

    if False:  # FIXME/2020-04-11: Implement or get off the pot!

        @catch_action_exception
        @ZoneContent.Decorators.reset_showing_help
        def fact_split(self, event):
            """"""
            self.carousel.controller.affirm(False)  # FIXME: Implement.

            self.zone_manager.rebuild_viewable()
            pass  # FIXME: Implement
            # FIXME/2019-01-15 13:51: For undo/redo, you'll need to leave
            # copy of new split Fact with copies of original Fact's
            # prev and next fact pointers, so that wires do not get crossed.

        @catch_action_exception
        @ZoneContent.Decorators.reset_showing_help
        def fact_erase(self, event):
            """"""
            # FIXME: Implement with undo, or provide other way to recover.
            self.carousel.controller.affirm(False)  # FIXME: Implement.
            self.zone_manager.rebuild_viewable()
            pass  # FIXME: Implement

        @catch_action_exception
        @ZoneContent.Decorators.reset_showing_help
        def fact_cut(self, event):
            """"""
            self.carousel.controller.affirm(False)  # FIXME: Implement.
            self.zone_manager.rebuild_viewable()
            pass  # FIXME: Implement

        @catch_action_exception
        @ZoneContent.Decorators.reset_showing_help
        def fact_merge_prev(self, event):
            """"""
            self.carousel.controller.affirm(False)  # FIXME: Implement.
            self.zone_manager.rebuild_viewable()
            pass  # FIXME: Implement

        @catch_action_exception
        @ZoneContent.Decorators.reset_showing_help
        def fact_merge_next(self, event):
            """"""
            self.carousel.controller.affirm(False)  # FIXME: Implement.
            self.zone_manager.rebuild_viewable()
            pass  # FIXME: Implement

    # ***

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def fact_copy_activity(self, event):
        """"""
        self.edits_manager.fact_copy_activity()
        self.zone_manager.update_status(_("Copied activity"))

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def fact_copy_tags(self, event):
        """"""
        self.edits_manager.fact_copy_tags()
        self.zone_manager.update_status(_("Copied tags"))

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def fact_copy_description(self, event):
        """"""
        self.edits_manager.fact_copy_description()
        self.zone_manager.update_status(_("Copied description"))

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def fact_copy_fact(self, event):
        """"""
        self.edits_manager.fact_copy_fact()
        self.zone_manager.update_status(_("Copied fact"))

    # ***

    @catch_action_exception
    @ZoneContent.Decorators.reset_showing_help
    def fact_paste(self, event):
        """"""
        def _fact_paste():
            paste_what = self.edits_manager.paste_copied_meta()
            hot_notif = paste_response(paste_what)
            self.zone_manager.update_status(hot_notif)

        def paste_response(paste_what):
            if not paste_what:
                return _("Nothing copied, nothing pasted")
            else:
                self.zone_manager.rebuild_viewable()
                return _("Pasted {0}").format(_(paste_what))

        _fact_paste()

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

    @catch_action_exception
    def edit_time_decrement_start(self, event):
        self.edit_time_adjust(-1, 'start')

    @catch_action_exception
    def edit_time_increment_start(self, event):
        self.edit_time_adjust(1, 'start')

    @catch_action_exception
    def edit_time_decrement_end(self, event):
        self.edit_time_adjust(-1, 'end')

    @catch_action_exception
    def edit_time_increment_end(self, event):
        self.edit_time_adjust(1, 'end')

    @catch_action_exception
    def edit_time_decrement_both(self, event):
        self.edit_time_adjust(-1, 'start', 'end')

    @catch_action_exception
    def edit_time_increment_both(self, event):
        self.edit_time_adjust(1, 'start', 'end')

    @catch_action_exception
    def edit_time_decrement_start_5min(self, event):
        self.edit_time_adjust(-5, 'start')

    @catch_action_exception
    def edit_time_increment_start_5min(self, event):
        self.edit_time_adjust(5, 'start')

    @catch_action_exception
    def edit_time_decrement_end_5min(self, event):
        self.edit_time_adjust(-5, 'end')

    @catch_action_exception
    def edit_time_increment_end_5min(self, event):
        self.edit_time_adjust(5, 'end')

    def edit_time_adjust(self, delta_mins, start_or_end, end_maybe=None):
        delta_time = self.edit_time_multiplier(delta_mins)
        self.edits_manager.edit_time_adjust(delta_time, start_or_end, end_maybe)
        self.edit_time_reset_refresh()

    def edit_time_reset_refresh(self):
        self.zone_manager.reset_diff_fact()
        self.zone_manager.selectively_refresh()

    # Hahaha, (lb): The time_adjust multiplier is a somewhat ridiculous feature.
    #   I'm not sure how useful it is.
    #   Especially if we still need a way for user to edit time directly!

    # (lb): If I hold down a key, I see about a ~ 33 msec. repeat.
    #   Which is probably "hardware settings"-settable per distro.
    #   If I repeatedly manually press a key, the fastest I can do
    #   is about 60 msecs. between presses (though it's more like
    #   100 msec. normally). So we'll try a threshold of 50 msecs.
    #   (Of course, 0.05 doesn't always work. Trying 100 msecs....)
    DOUBLE_KEYLICK_THRESHOLD = 0.10
    MULTIPLY_BY_05_THRESHOLD = 45
    MULTIPLY_BY_10_THRESHOLD = 90
    MULTIPLY_BY_30_THRESHOLD = 150
    MULTIPLY_BY_60_THRESHOLD = 240
    MULTIPLY_BY_1440_THRESHOLD = 375
    MULTIPLY_BY_10080_THRESHOLD = 500
    MULTIPLY_BY_525960_THRESHOLD = 700

    def edit_time_multiplier(self, delta_mins):
        # MEH: (lb): Ideally, we'd hook a global PPT key handler so
        # we could clear the last time_adjust time if a non time_adjust
        # key is pressed; or clear it after some timeout. Whatever; this
        # code has same outcome, even if it doesn't feel ideal.
        if (
            self.last_time_time_adjust is None
            # Be aware of the OS hardware delay before a long press becomes a
            # repeat event, and ignore elapsed time before 1st and 2nd events.
            or (
                self.press_cnt_time_adjust > 1
                and (
                    (time.time() - self.last_time_time_adjust)
                    > UpdateHandler.DOUBLE_KEYLICK_THRESHOLD
                )
            )
        ):
            self.last_time_time_adjust = None
            self.press_cnt_time_adjust = 0
            delta_time = timedelta(minutes=delta_mins * 1)
        elif self.press_cnt_time_adjust < UpdateHandler.MULTIPLY_BY_05_THRESHOLD:
            delta_time = timedelta(minutes=delta_mins * 1)
        elif self.press_cnt_time_adjust < UpdateHandler.MULTIPLY_BY_10_THRESHOLD:
            delta_time = timedelta(minutes=delta_mins * 5)
        elif self.press_cnt_time_adjust < UpdateHandler.MULTIPLY_BY_30_THRESHOLD:
            delta_time = timedelta(minutes=delta_mins * 10)
        elif self.press_cnt_time_adjust < UpdateHandler.MULTIPLY_BY_60_THRESHOLD:
            delta_time = timedelta(minutes=delta_mins * 30)
        elif self.press_cnt_time_adjust < UpdateHandler.MULTIPLY_BY_1440_THRESHOLD:
            delta_time = timedelta(hours=delta_mins)
        elif self.press_cnt_time_adjust < UpdateHandler.MULTIPLY_BY_10080_THRESHOLD:
            delta_time = timedelta(days=delta_mins)
        elif self.press_cnt_time_adjust < UpdateHandler.MULTIPLY_BY_525960_THRESHOLD:
            delta_time = timedelta(weeks=delta_mins)
        else:
            delta_time = timedelta(minutes=delta_mins * 60 * 8760)
        self.last_time_time_adjust = time.time()
        self.press_cnt_time_adjust += 1
        return delta_time

    # ***

    @catch_action_exception
    def edit_fact(self, event):
        """"""
        self.carousel.enduring_edit = True
        event.app.exit()

    def exit_to_awesome_prompt(self, event, restrict_edit):
        self.carousel.enduring_edit = True
        self.carousel.restrict_edit = restrict_edit
        event.app.exit()

    @catch_action_exception
    def edit_actegory(self, event):
        """"""
        self.exit_to_awesome_prompt(event, 'actegory')

    @catch_action_exception
    def edit_tags(self, event):
        """"""
        self.exit_to_awesome_prompt(event, 'tags')

    @catch_action_exception
    def edit_description(self, event):
        """"""
        self.exit_to_awesome_prompt(event, 'description')

    # ***

    def _key_sequence_str(self, event):
        # For normal characters, we could grab event.data, but for combos,
        # use key_sequence for readability. E.g., if combo is ('X', 'c-c'),
        # event.data == '\x03', but joining key_sequences gives 'Xc-c'.
        return ''.join(seq.key for seq in event.key_sequence)

    @catch_action_exception
    def begin_commando(self, event):
        """"""
        self.began_commando = self._key_sequence_str(event)
        self.typed_commando = ''
        self.zone_manager.zone_lowdown.update_status(
            self.began_commando,
            clear_after_secs=0,
        )
        self.carousel.action_manager.wire_keys_commando()

    @catch_action_exception
    def parts_commando(self, event):
        """"""
        self.typed_commando += self._key_sequence_str(event)
        self.zone_manager.zone_lowdown.update_status(
            self.began_commando + self.typed_commando,
            clear_after_secs=0,
        )

    @catch_action_exception
    def final_commando(self, event):
        """"""
        hot_notif = self.colon_commando(event, self.typed_commando)
        del self.began_commando
        del self.typed_commando
        if hot_notif:
            self.zone_manager.zone_lowdown.update_status(hot_notif)
        else:
            self.zone_manager.zone_lowdown.reset_status()
        self.carousel.action_manager.unwire_keys_commando()

    def colon_commando(self, event, typed_commando):
        if not typed_commando:
            return
        keys_config = self.carousel.controller.config['editor-keys']
        if typed_commando == keys_config['write_commando']:
            # E.g., `:w`.
            self.carousel.save_edited_and_live(event)
        elif typed_commando == keys_config['quit_commando']:
            # E.g., `:q`.
            self.carousel.cancel_command(event)
        elif typed_commando == keys_config['save_quit_commando']:
            self.carousel.save_edited_and_exit(event)
        else:
            # (lb): Copying Vim's message for now. Verbatim. Don't judge.
            msg = 'E492: Not an editor command: {}'.format(typed_commando)
            return msg

    # ***

    @catch_action_exception
    def begin_delta_time_start(self, event):
        """"""
        self.carousel.action_manager.wire_keys_delta_time()
        self.typed_delta_time = ''
        self.delta_time_gap_okay = False
        self.delta_time_target = 'end'

    @catch_action_exception
    def begin_delta_time_end(self, event):
        """"""
        self.carousel.action_manager.wire_keys_delta_time()
        self.typed_delta_time = ''
        self.delta_time_gap_okay = False
        self.delta_time_target = 'start'

    RE_NUMERIC = re.compile('^[0-9]$')

    @catch_action_exception
    def parts_delta_time(self, event):
        """"""
        # If user pressed allow-gap key already (e.g., '!'), do not allow
        # more time to be entered; be strict and reset instead.
        if self.delta_time_gap_okay:
            # Because gap_okay only set true on '!', means input error.
            self.reset_delta_time()
        # We could allow any character and then parse at error, potentially
        # showing an error message. Or, if user types non-number now, we
        # could just go back to old state. -- It's not completely silent,
        # as the cursor will reappear.
        elif event.data == '.':
            if '.' in self.typed_delta_time:
                # So strict!
                self.reset_delta_time()
            else:
                self.typed_delta_time += '.'
        elif UpdateHandler.RE_NUMERIC.match(event.data):
            self.typed_delta_time += event.data
        else:
            self.reset_delta_time()

    @catch_action_exception
    def allow_time_gap(self, event):
        """"""
        self.delta_time_gap_okay = True

    @catch_action_exception
    def final_delta_time_apply(self, event):
        """"""
        self.apply_delta_time(event, scalar=1)

    @catch_action_exception
    def final_delta_time_minutes(self, event):
        """"""
        self.apply_delta_time(event, scalar=1)

    @catch_action_exception
    def final_delta_time_hours(self, event):
        """"""
        self.apply_delta_time(event, scalar=60)

    def apply_delta_time(self, event, scalar):
        try:
            delta_time = float(self.typed_delta_time)
        except ValueError:
            # No period.
            delta_time = int(self.typed_delta_time)
        delta_mins = timedelta(minutes=delta_time * scalar)

        edit_fact = self.edits_manager.editable_fact()
        if self.delta_time_target == 'end':
            apply_time = edit_fact.start + delta_mins
        else:  # == 'start'
            end_time = edit_fact.end or self.carousel.controller.now
            apply_time = end_time - delta_mins

        self.edits_manager.edit_time_adjust(
            apply_time,
            self.delta_time_target,
            gap_okay=self.delta_time_gap_okay,
        )
        self.edit_time_reset_refresh()
        self.reset_delta_time()

    @catch_action_exception
    def panic_delta_time(self, event):
        """"""
        self.reset_delta_time()

    def reset_delta_time(self):
        del self.typed_delta_time
        del self.delta_time_gap_okay
        del self.delta_time_target
        self.carousel.action_manager.unwire_keys_delta_time()

