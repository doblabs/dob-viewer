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
"""Facts Carousel Header (Fact meta and diff)"""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

from prompt_toolkit.enums import EditingMode
from prompt_toolkit.layout.containers import HSplit, VSplit, to_container
from prompt_toolkit.widgets import Label, TextArea

from nark.helpers.parse_time import parse_dated

from .dialog_overlay import show_message
from ..helpers.exceptions import catch_action_exception
from ..helpers.fix_times import (
    insert_forcefully,
    must_complete_times,
    resolve_overlapping,
    DEFAULT_SQUASH_SEP
)

__all__ = [
    'ZoneDetails',
]


class ZoneDetails(object):
    """"""
    def __init__(self, carousel):
        self.carousel = carousel
        self.active_widgets = None

    class HeaderKeyVal(object):
        def __init__(
            self,
            index,
            fact_attr=None,
            diff_kwargs=None,
            key_parts=None,
            val_label=None,
            text_area=None,
            orig_val=None,
        ):
            self.index = index
            self.fact_attr = fact_attr
            self.diff_kwargs = diff_kwargs
            self.key_parts = key_parts
            self.val_label = val_label
            self.text_area = text_area
            self.orig_val = orig_val

    def standup(self):
        pass

    # ***

    def rebuild_viewable(self):
        """"""
        def _rebuild_viewable():
            self.facts_diff = self.carousel.zone_manager.facts_diff
            assemble_children()
            self.details_container = build_container()
            self.refresh_all_children()
            return self.details_container

        def assemble_children():
            self.children = []
            add_meta_lines()

        def add_meta_lines():
            # Skipping: add_header_midpoint.
            add_header_duration()
            add_header_start_time()
            add_header_end_time()
            # Skipping: add_header_fact_pk.
            # Skipping: add_header_deleted.
            # Skipping: add_header_split_from.
            add_header_activity()
            add_header_category()
            add_header_tags()
            add_blank_line()

        # ***

        def add_header_duration():
            self.label_duration = add_header_parts('duration')

        def add_header_start_time():
            self.widgets_start = add_header_parts(
                'start', 'start_fmt_local', editable=True,
            )

        def add_header_end_time():
            self.widgets_end = add_header_parts(
                'end', 'end_fmt_local_nowwed', editable=True,
            )

        def add_header_activity():
            self.widgets_activity = add_header_parts('activity', 'activity_name')

        def add_header_category():
            self.widgets_category = add_header_parts('category', 'category_name')

        def add_header_tags():
            self.widgets_tags = add_header_parts(
                'tags',
                'tags_tuples',
                split_lines=True,
                colorful=True,
                underlined=True,
            )

        def add_blank_line():
            self.children.append(self.make_header_label(''))

        # ***

        def add_header_parts(show_name, fact_attr=None, editable=False, **kwargs):
            keyval_parts = ZoneDetails.HeaderKeyVal(
                index=len(self.children),
                fact_attr=fact_attr,
                diff_kwargs=kwargs,
                key_parts=self.make_header_name_parts(show_name),
                val_label=self.make_header_label(),
                text_area=TextArea(height=1) if editable else None,
            )
            self.children.append(
                VSplit(
                    children=[
                        *keyval_parts.key_parts,
                        keyval_parts.val_label,
                    ],
                )
            )
            return keyval_parts

        # ***

        def build_container():
            details_container = HSplit(children=self.children)
            return details_container

        # ***

        return _rebuild_viewable()

    # ***

    def refresh_all_children(self):
        self.refresh_duration()
        self.refresh_time_start()
        self.refresh_time_end()
        self.refresh_activity()
        self.refresh_category()
        self.refresh_tags()

    # ***

    def selectively_refresh(self):
        # We don't need to refresh except for ongoing fact.
        orig_fact = self.facts_diff.orig_fact
        edit_fact = self.facts_diff.edit_fact
        if (orig_fact.end is not None) and (edit_fact.end is not None):
            return
        # Update times and spans based off <now>.
        self.refresh_duration()
        self.refresh_time_end()

    # ***

    def refresh_duration(self):
        orig_val, edit_val = self.facts_diff.diff_time_elapsed(show_now=True)
        diff_tuples = self.facts_diff.diff_line_tuples_style(orig_val, edit_val)
        self.label_duration.val_label.text = diff_tuples

    def refresh_time_start(self):
        self.refresh_val_widgets(self.widgets_start)

    def refresh_time_end(self):
        self.refresh_val_widgets(self.widgets_end)

    def refresh_activity(self):
        self.refresh_val_widgets(self.widgets_activity)

    def refresh_category(self):
        self.refresh_val_widgets(self.widgets_category)

    def refresh_tags(self):
        self.refresh_val_widgets(self.widgets_tags)

    def refresh_val_widgets(self, keyval_widgets):
        self.carousel.controller.affirm(keyval_widgets.fact_attr)
        diff_tuples = self.facts_diff.diff_attrs(
            keyval_widgets.fact_attr, **keyval_widgets.diff_kwargs
        )
        keyval_widgets.val_label.text = diff_tuples

    # ***

    def replace_val_container(self, val_container, keyval_widgets, label_class):
        keyval_container = self.details_container.get_children()[keyval_widgets.index]
        key_label = keyval_container.get_children()[1]
        key_label.style = label_class
        keyval_vsplit = self.details_container.get_children()[keyval_widgets.index]
        keyval_vsplit.get_children()[3] = to_container(val_container)

    def replace_val_container_label(self, keyval_widgets):
        self.replace_val_container(
            keyval_widgets.val_label, keyval_widgets, 'class:header',
        )

    def replace_val_container_text_area(self, keyval_widgets):
        self.replace_val_container(
            keyval_widgets.text_area, keyval_widgets, 'class:header-focus',
        )

    # ***

    @catch_action_exception
    def edit_time_start(self, event=None, focus=True):
        if focus:
            edit_fact = self.facts_diff.edit_fact
            start_fmt_local = edit_fact.start_fmt_local
            self.widgets_start.orig_val = start_fmt_local
            self.widgets_start.text_area.text = start_fmt_local
            self.edit_time_focus(self.widgets_start)
            return True
        else:
            return self.edit_time_leave(self.widgets_start)

    @catch_action_exception
    def edit_time_end(self, event=None, focus=True):
        if focus:
            edit_fact = self.facts_diff.edit_fact
            end_fmt_local_or_now = edit_fact.end_fmt_local_or_now
            self.widgets_end.orig_val = end_fmt_local_or_now
            self.widgets_end.text_area.text = end_fmt_local_or_now
            self.edit_time_focus(self.widgets_end)
            return True
        else:
            return self.edit_time_leave(self.widgets_end)

    # ***

    def edit_time_focus(self, keyval_widgets):
        self.active_widgets = keyval_widgets
        # Swap out a container in the layout.
        self.replace_val_container_text_area(keyval_widgets)
        # Focus the newly placed container.
        self.carousel.zone_manager.layout.focus(keyval_widgets.text_area)
        # Move the cursor to the end of the exit field,
        # e.g., if there's a date and time already set,
        # put the cursor after it all.
        self.send_cursor_right_to_end(keyval_widgets.text_area.buffer)
        # Wire a few simple bindings for editing (mostly rely on PPT's VI mode.)
        self.carousel.action_manager.wire_keys_edit_time()
        # (lb): Will VI mode be useful? Perhaps for a little easy `r`eplace,
        # among other helpful features? Note that you gotta 'escape' first.
        self.carousel.zone_manager.application.editing_mode = EditingMode.VI

    # ***

    def edit_time_leave(self, keyval_widgets):
        def _edit_time_leave():
            self.carousel.controller.affirm(
                (self.active_widgets is None)
                or (keyval_widgets is self.active_widgets)
            )
            return apply_edited_and_refresh()

        def apply_edited_and_refresh():
            leave_okayed = not was_edited()
            if not leave_okayed:
                leave_okayed = self.editable_text_enter(passive=True)
            if not leave_okayed:
                return False
            return refresh_keyval()

        def was_edited():
            self.carousel.controller.client_logger.warning(
                'orig_val: {}'.format(keyval_widgets.orig_val)
            )
            return keyval_widgets.text_area.text != keyval_widgets.orig_val

        def refresh_keyval():
            # Refresh labels now, so that old value isn't shown briefly and then
            # updated, which looks weird. Rather, update label first, then show.
            self.selectively_refresh()
            self.replace_val_container_label(self.active_widgets)
            self.carousel.zone_manager.application.editing_mode = None
            self.active_widgets = None
            return True

        return _edit_time_leave()

    # ***

    def send_cursor_right_to_end(self, winbufr):
        end_posit = winbufr.document.get_end_of_document_position()
        # Generally same as: winbufr.document.get_end_of_line_position()
        winbufr.cursor_right(end_posit)

    # ***

    def editable_text_any_key(self, event=None):
        self.carousel.controller.client_logger.debug('event: {}'.format(event))
        # Ignore all alpha characters except those for [t|T]imezone delimiter.
        if event.data.isalpha() and event.data not in ('t', 'T'):
            return
        # Like PPT's basic binding's filter=insert_mode, or vi's filter=vi_replace_mode.
        # "Insert data at cursor position."
        # PPT basic binding's self-insert:
        #   event.current_buffer.insert_text(event.data * event.arg)
        # PPT vi binding's vi_replace_mode:
        #  event.current_buffer.insert_text(event.data, overwrite=True)
        event.current_buffer.insert_text(event.data)
        self.editable_was_edited = True

    # ***

    @catch_action_exception
    def editable_text_enter(self, event=None, passive=False):
        """"""
        leave_okayed = [True, ]

        def _editable_text_enter():
            edit_text = self.active_widgets.text_area.text
            # Note that carousel.edits_manager.curr_edit returns fact-under-edit
            # only if one already exists, but fact may be unedited, in which case
            # it'd return the original, unedited fact. So use the editable fact we
            # made earlier.
            edit_fact = self.facts_diff.edit_fact
            apply_edited_time(edit_fact, edit_text)
            return leave_okayed[0]

        def apply_edited_time(edit_fact, edit_text):
            if not edit_text:
                apply_edit_time_removed(edit_fact)
            else:
                apply_edit_time_changed(edit_fact, edit_text)

        # ***

        def apply_edit_time_removed(edit_fact):
            if self.active_widgets is self.widgets_start:
                apply_edit_time_removed_start(edit_fact)
            else:
                self.carousel.controller.affirm(self.active_widgets is self.widgets_end)
                apply_edit_time_removed_end(edit_fact)

        def apply_edit_time_removed_start(edit_fact):
            # Nothing ventured, nothing gained. Ignore deleted start. (We could
            # instead choose to do nothing, or choose to warn-tell user they're
            # an idiot and cannot clear the start time, or we could just behave
            # like a successful edit (by moving focus back to the matter (Fact
            # description) control) but not actually edit anything. Or we could
            # just do nothing. (User can tab-away and then we'll repopulate we
            # unedited time.)
            self.carousel.controller.affirm(edit_fact.start is not None)
            self.widgets_start.text_area.text = edit_fact.start_fmt_local
            if passive:
                # User is tabbing away. We've reset the start, so let them.
                return
            # User hit 'enter'. Annoy them with a warning.
            show_message_cannot_clear_start()

        def apply_edit_time_removed_end(edit_fact):
            if edit_fact.end is None:
                # Already cleared; nothing changed.
                return
            if not self.carousel.controller.is_final_fact(edit_fact):
                self.widgets_end.text_area.text = edit_fact.end_fmt_local_or_now
                # Always warn user, whether they hit 'enter' or are tabbing away.
                show_message_cannot_clear_end()
            else:
                edit_fact.end = None
                self.carousel.controller.affirm(False)

        # ***

        def apply_edit_time_changed(edit_fact, edit_text):
            time_now = self.carousel.controller.now
            edit_time = parse_dated(edit_text, time_now, cruftless=True)
            if edit_time is None:
                show_message_cannot_parse_time(edit_text)
            else:
                apply_edit_time_valid(edit_fact, edit_time)

        def apply_edit_time_valid(edit_fact, edit_time):
            was_fact = edit_fact.copy()
            if self.active_widgets is self.widgets_start:
                applied = apply_edit_time_start(edit_fact, edit_time)
            else:
                self.carousel.controller.affirm(self.active_widgets is self.widgets_end)
                applied = apply_edit_time_end(edit_fact, edit_time)
            check_conflicts_and_confirm(edit_fact, was_fact, applied)

        def apply_edit_time_start(edit_fact, edit_time):
            if edit_fact.start == edit_time:
                return False
            edit_fact.start = edit_time
            return True

        def apply_edit_time_end(edit_fact, edit_time):
            if edit_fact.end == edit_time:
                return False
            edit_fact.end = edit_time
            return True

        def check_conflicts_and_confirm(edit_fact, was_fact, applied):
            if not applied:
                # Nothing changed; no-op.
                return
            edited_fact_check_conflicts(edit_fact, was_fact)

        def edited_fact_check_conflicts(edit_fact, was_fact):
            conflicts = edited_fact_conflicts(edit_fact)
            if not ask_user_confirm_conflicts(conflicts):
                # Not confirmed! Leave the edit widget date unchanged.
                edit_fact = was_fact
                return
            allow_momentaneous = self.carousel.controller.config['allow_momentaneous']
            # FIXME: Do not ignore return value, resolved/edited_conflicts.
            resolve_overlapping(
                edit_fact,
                conflicts,
                squash_sep='??',
                allow_momentaneous=allow_momentaneous,
            )
            conflicts = insert_forcefully(
                self.carousel.controller, edit_fact, DEFAULT_SQUASH_SEP,
            )
            if not ask_user_confirm_conflicts(conflicts):
                # Not confirmed! Leave the edit widget date unchanged.
                edit_fact = was_fact
                return
            edits_manager = self.carousel.edits_manager
            edits_manager.add_undoable([was_fact], what='header-edit')
            edits_manager.apply_edits(edit_fact)
            edited_fact_update_label_text()

        def edited_fact_conflicts(edit_fact):
            conflicts = must_complete_times(
                self.carousel.controller,
                new_facts=[edit_fact],
                progress=None,
                ongoing_okay=True,
                leave_blanks=True,
                other_edits={},
                suppress_barf=True,
            )
            return conflicts

        def ask_user_confirm_conflicts(conflicts):
            if not conflicts:
                return True
            # FIXME: Implement this.
            return False

        def edited_fact_update_label_text():
            if self.active_widgets is self.widgets_start:
                diff_tuples = self.facts_diff.diff_attrs('start_fmt_local')
            else:
                self.carousel.controller.affirm(self.active_widgets is self.widgets_end)
                diff_tuples = self.facts_diff.diff_attrs('end_fmt_local_nowwed')
            self.active_widgets.val_label.text = diff_tuples

        # ***

        def show_message_cannot_clear_start():
            show_message_and_deny_leave(
                self.carousel.zone_manager.root,
                _('Try again'),
                _(
                    "You may not clear a Fact's start time.\n\n"
                    "Enter a valid date and time, clock time, or relative time."
                ),
            )

        def show_message_cannot_clear_end():
            show_message_and_deny_leave(
                self.carousel.zone_manager.root,
                _('You lose'),
                _("You may not clear a Fact's end time unless it is the final Fact."),
            )

        def show_message_cannot_parse_time(edit_text):
            show_message_and_deny_leave(
                self.carousel.zone_manager.root,
                _('Wah wah'),
                _("Did not compute: {0}").format(edit_text),
            )

        def show_message_and_deny_leave(*args, **kwargs):
            leave_okayed[0] = False
            show_message(*args, **kwargs)

        # ***

        def re_focus_maybe():
            if passive:
                # User is tabbing; caller is handling focus.
                return
            self.zone_content.focus_content()

        # ***

        return _editable_text_enter()

    # ***

    @catch_action_exception
    def undo_command(self, event):
        # FIXME/2019-01-21: Is this correct? Use case:
        #   - Press 'e'; edit 'end'; press Enter to apply change.
        #   - Press 'e' again; edit 'end'; press Ctrl-z.
        #   - Expect: previous (intermediate) end time, not original end time!
        #   - For original end time: press 'R' reset!
        orig_fact = self.facts_diff.orig_fact
        # FIXME/2019-01-14 18:11: Localization/l10n/timezone'ation...
        #                           start_fmt_local vs start_fmt_utc, and end...
        # When editing, reset widget to unedited time (do not go through undo stack).
        if self.active_widgets is self.widgets_start:
            event.current_buffer.text = orig_fact.start_fmt_local
        elif self.active_widgets is self.widgets_end:
            event.current_buffer.text = orig_fact.end_fmt_local

    @catch_action_exception
    def redo_command(self, event):
        # We could restore the edited time that the user undid.
        # But there's not much utility in that.
        pass

    # ***

    def make_header_label(self, header_text='', dont_extend_width=False):
        return Label(
            text=header_text,
            style='class:header',
            dont_extend_width=dont_extend_width,
        )

    def make_header_name_parts(self, name=''):
        prefix = '  '
        padded = '{:.<19}'.format(name)
        kv_sep = ' : '

        labels = [
            self.make_header_label(prefix, dont_extend_width=True),
            self.make_header_label(padded, dont_extend_width=True),
            self.make_header_label(kv_sep, dont_extend_width=True),
        ]
        return labels

