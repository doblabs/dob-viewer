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

"""Facts Carousel Header (Fact meta and diff)"""

from gettext import gettext as _

from datetime import datetime
import re

from prompt_toolkit.application.current import get_app
from prompt_toolkit.layout.containers import HSplit, VSplit, to_container
from prompt_toolkit.lexers import SimpleLexer
from prompt_toolkit.widgets import Label, TextArea

from nark.helpers.parse_errors import ParserInvalidDatetimeException
from nark.helpers.parse_time import parse_dated

from ..crud.fix_times import must_complete_times

from ..ptkui.dialog_overlay import show_message

from .exceptions import catch_action_exception
from .zone_details_time_end import ZoneDetails_TimeEnd
from .zone_details_time_start import ZoneDetails_TimeStart

__all__ = (
    'ZoneDetails',
)


class ZoneDetails(
    ZoneDetails_TimeStart,
    ZoneDetails_TimeEnd,
):
    """"""
    def __init__(self, carousel):
        super(ZoneDetails, self).__init__()
        self.carousel = carousel
        self.active_widgets = None
        # Convenience attrs.
        self.affirm = self.carousel.controller.affirm

    class HeaderKeyVal(object):
        """"""
        def __init__(
            self,
            index,
            what_part=None,
            fact_attr=None,
            diff_kwargs=None,
            key_parts=None,
            val_label=None,
            text_area=None,
            orig_val=None,
            mouse_handler=None,
        ):
            self.index = index
            self.what_part = what_part
            self.fact_attr = fact_attr
            self.diff_kwargs = diff_kwargs
            self.key_parts = key_parts
            self.val_label = val_label
            self.text_area = text_area
            self.orig_val = orig_val
            self.mouse_handler = mouse_handler

    # ***

    def standup(self):
        """"""
        def _standup():
            # A couple convenience attrs.
            self.zone_manager = self.carousel.zone_manager
            self.zone_content = self.carousel.zone_manager.zone_content
            assemble_children()
            self.details_container = build_container()

        def assemble_children():
            self.children = []
            add_meta_lines()

        def add_meta_lines():
            # Skipping: add_header_midpoint.
            add_header_duration()
            self.add_header_start_time()
            self.add_header_end_time()
            # Skipping: add_header_fact_pk.
            # Skipping: add_header_deleted.
            # Skipping: add_header_split_from.
            add_header_activity()
            add_header_category()
            add_header_tags()
            add_blank_line()

        # ***

        def add_header_duration():
            # MEH/2019-11-22: (lb): Duration label mouse handler, but to do what?
            # - User clicks, modal asks for new duration, adjust end time to match?
            self.label_duration = self.add_header_section('duration')

        def add_header_activity():
            self.widgets_activity = self.add_header_section(
                'activity',
                'activity_name',
                mouse_handler=header_widget_mouse_handler('actegory'),
            )

        def add_header_category():
            self.widgets_category = self.add_header_section(
                'category',
                'category_name',
                mouse_handler=header_widget_mouse_handler('actegory'),
            )

        def add_header_tags():
            # FIXME/BACKLOG/2018-07-19: Long tags can extend width,
            #   but do not wrap the line. Need to manually break?
            #   See: wrap_on_whitespace_maybe
            # FIXME/2018-07-28: Fix tags display: with 2+ tags, inserting
            #   newlines makes the height dance. But keeping for now, as not
            #   many Facts (o' mine) with two or more tags.
            self.widgets_tags = self.add_header_section(
                'tags',
                'tags_tuples',
                split_lines=True,
                colorful=True,
                underlined=True,
                mouse_handler=header_widget_mouse_handler('tags'),
            )

        def add_blank_line():
            self.blank_line = self.make_section_component('', style='class:blank-line')
            # Note: Somewhere else we set widget.formatted_text_control.style,
            # but here it's widget.window.style we want.
            # Note: Also that blank_line.window.style has one PPT default
            # style and also a style from our code, i.e.,
            #   blank_line.window.style: 'class:label class:title-normal'
            self.blank_line.window.style = 'class:blank-line '
            self.children.append(self.blank_line)

        # ***

        def build_container():
            details_container = HSplit(children=self.children)
            return details_container

        # ***

        def header_widget_mouse_handler(restrict_edit):
            def _mouse_handler(mouse_event):
                # MAYBE/2019-11-22: (lb): Interesting feature, but jarring:
                # - User could click on Activity name in header, or Category,
                # or Tags, and app could respond by showing Awesome Prompt.
                # However, this behavior is rather jarring if you're not
                # expecting it.
                # - Also, user might be trying to click and drag to select
                # the Activity or Category name, but immediately on mouse
                # down the Awesome Prompt is shown (this callback is called),
                # and PPT doesn't seem to bother sending us more than a single
                # mouse down. So unless PPT updated to not trigger callback
                # if user either selecting text or double clicking, and to
                # only trigger callback on simple, non-drag press and release,
                # this feature should only be enabled if user wants it on.
                # - MAYBE/2019-11-22: (lb): Maybe add config option to enable.
                #   Until then, disabled by way of hidden branching.
                if False:
                    self.carousel.enduring_edit = True
                    self.carousel.restrict_edit = restrict_edit
                    get_app().exit()
            return _mouse_handler

        # ***

        _standup()

    # ***

    def rebuild_viewable(self):
        """"""
        self.refresh_all_children()
        return self.details_container

    # ***

    def add_header_section(
        self,
        part_type,
        fact_attr=None,
        editable=False,
        mouse_handler=None,
        **kwargs
    ):
        text_area = None
        if editable:
            # 2019-11-22: (lb): Some PPT controls have focus options, e.g.,
            #   TextArea(..., focusable=True, focus_on_click=True)
            # but the Carousel handles changing focus, so we instead
            # register a mouse handler to change the focus ourselves.
            # (diff_attrs() wires the handler using the third element
            # of the ubiquitous (style, text) tuples). Note also that
            # I tried options, focusable=True and focus_on_click=True,
            # and nothing.
            # (lb): I tried making a custom lexer, e.g., class MyLexer(Lexer),
            # but for whatever reason, the `assert isinstance(lexer, Lexer)`
            # in PPT's DynamicLexer fails, because the custom lexer object
            # somehow reports lexer.__class__: abc.ABCMeta. Fortunately,
            # rather than trying to explain how the lexer object gets
            # converted into some meta wrapper thing, we can use a builtin
            # lexer that simply styles the input text.
            text_area = TextArea(
                height=1,
                lexer=SimpleLexer(style='class:value-focus'),
            )

        keyval_parts = ZoneDetails.HeaderKeyVal(
            index=len(self.children),
            what_part=part_type,
            fact_attr=fact_attr,
            diff_kwargs=kwargs,
            key_parts=self.make_header_label_parts(part_type),
            val_label=self.make_header_value_part(part_type),
            text_area=text_area,
            mouse_handler=mouse_handler,
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

    def make_header_label_parts(self, part_type=''):
        name = _(part_type)
        prefix = '  '
        padded = '{:.<19}'.format(name)
        kv_sep = ' : '

        tline_style = 'class:title-normal-line'
        title_style = 'class:title-normal-line class:title-normal'

        labels = [
            self.make_section_component(
                prefix, style=tline_style, dont_extend_width=True,
            ),
            self.make_section_component(
                padded, style=title_style, dont_extend_width=True,
            ),
            self.make_section_component(
                kv_sep, style=tline_style, dont_extend_width=True,
            ),
        ]
        return labels

    def make_header_value_part(self, part_type=''):
        style = 'class:value-normal-line '
        if part_type:
            style += 'class:value-{}-line '.format(part_type)
        return self.make_section_component('', style=style)

    # ***

    def make_section_component(
        self, header_text='', style='', dont_extend_width=False,
    ):
        # The header label is called once when first showing the Fact,
        # and not called during the rebuild_viewable heartbeat. It's
        # not even rebuilt when focus changes between components.
        label = Label(
            text=header_text,
            style=style,
            dont_extend_width=dont_extend_width,
        )
        return label

    # ***

    def refresh_all_children(self):
        self.refresh_duration()
        self.refresh_time_start()
        self.refresh_time_end()
        self.refresh_activity()
        self.refresh_category()
        self.refresh_tags()
        self.refresh_blank_line()

    # ***

    def selectively_refresh(self):
        # Update times and spans based off <now>.
        self.refresh_duration()
        # Update start time, should its time have been adjusted.
        self.refresh_time_start()
        # Update the <now> time duration that FactsDiff shows.
        self.refresh_time_end()

    # ***

    def refresh_duration(self):
        # The style_class is 'class:value-normal class:value-duration '.
        style_class = self.assemble_style_class_for_part(self.label_duration)
        orig_val, edit_val = self.zone_manager.facts_diff.diff_time_elapsed(
            show_now=True, style_class=style_class,
        )
        diff_tuples = self.zone_manager.facts_diff.diff_line_tuples_style(
            orig_val, edit_val, style_class=style_class,
        )
        self.label_duration.val_label.text = diff_tuples
        self.add_stylable_classes(self.label_duration)

    def refresh_activity(self):
        self.refresh_val_widgets(self.widgets_activity)

    def refresh_category(self):
        self.refresh_val_widgets(self.widgets_category)

    def refresh_tags(self):
        self.refresh_val_widgets(self.widgets_tags)

    def refresh_blank_line(self):
        # Lets the user override the blank line style for matching rules.
        custom_classes = self.carousel.add_stylable_classes(
            ppt_widget=None, friendly_name='blank-line',
        )
        # (lb): I'm wondering if we should just clobber style, not append
        # (and do so other places we fiddle with style).
        # Probably not necessary:
        #   self.blank_line.window.style = 'class:blank-line ' + custom_classes
        self.blank_line.window.style = custom_classes or 'class:blank-line '

    def refresh_val_widgets(self, keyval_widgets):
        self.affirm(keyval_widgets.fact_attr)
        # The style_class is 'class:value-normal class:value-{activity|category|etc} '.
        style_class = self.assemble_style_class_for_part(keyval_widgets)
        diff_tuples = self.zone_manager.facts_diff.diff_attrs(
            keyval_widgets.fact_attr,
            style_class=style_class,
            mouse_handler=keyval_widgets.mouse_handler,
            **keyval_widgets.diff_kwargs
        )
        keyval_widgets.val_label.text = diff_tuples
        # We've already set the default value (on top of PPT's Label default class):
        #   keyval_widgets.val_label.window.style:
        #     'class:label class:value-normal-line'
        # and now we'll set value-{normal|activity|category|etc}[-line], if rules apply.
        # (lb): Note also widgets_start and widgets_end come through here.
        self.add_stylable_classes(keyval_widgets)

    def assemble_style_class_for_part(self, keyval_widgets):
        style_class = 'class:value-normal '
        style_class += 'class:value-{} '.format(keyval_widgets.what_part)
        return style_class

    def add_stylable_classes(self, keyval_parts, set_focus=None):
        self.add_stylable_classes_header_titles(keyval_parts, set_focus)
        self.add_stylable_classes_header_values_normal(keyval_parts)
        self.add_stylable_classes_header_values_focus(keyval_parts, set_focus)

    def add_stylable_classes_header_titles(self, keyval_parts, set_focus=None):
        # keyval_parts.key_parts is a list of Labels (from make_header_label_parts).
        # - The first item is the left column padding. E.g.: '  '.
        # - The second item is the meta label and the ...-padding.
        # - The third item is the middle column, ' : ', before the value.
        # (lb): This is another 'MEH' moment: How much customizability
        #   do we really need? Or, put another way, we can always add
        #   more later. For now, it seems like enough to be able to both
        #   customize the inner meta label (including the .-padding), or
        #   to customize the whole meta line. I don't see a need (or, I
        #   don't have a need) to customize the left or center column bits.
        #   (Also, you can customize specially when focused, so there are
        #   already four ways to customize each header title.)
        if set_focus is None and self.active_widgets is keyval_parts:
            set_focus = True
        dot_padded_title = keyval_parts.key_parts[1]
        title_part = 'title-{}'.format(keyval_parts.what_part)
        if not set_focus:
            friendlies = ['title-normal', title_part]
        else:
            # This keyval_parts should be editable.
            self.affirm(keyval_parts.text_area is not None)
            friendlies = ['title-focus', title_part + '-focus']

        for friendly_name in friendlies:
            # Register the -line style, which means assigns same style to all parts.
            for label in keyval_parts.key_parts:
                self.carousel.add_stylable_classes(label, friendly_name + '-line')
            # Register title-[normal|duration|start|end|activity|category|tags][-focus]
            # on just the title label part of the header.
            self.carousel.add_stylable_classes(dot_padded_title, friendly_name)

    def add_stylable_classes_header_values_normal(self, keyval_parts):
        # For matching rules, apply any stylits for: value-normal, value-normal-line,
        # and value-[duration|start|end|activity|category|tags][-line]
        value_part = 'value-{}'.format(keyval_parts.what_part)
        for friendly_name in ('value-normal', value_part):
            for suffix in ('-line', ''):
                self.carousel.add_stylable_classes(
                    keyval_parts.val_label,
                    friendly_name + suffix,
                )

    def add_stylable_classes_header_values_focus(self, keyval_parts, set_focus=False):
        if not set_focus:
            return

        # For matching rules, apply any stylits for:
        # value-focus, value-focus-line, and value-[start|end]-focus[-line].
        value_part = 'value-{}-focus'.format(keyval_parts.what_part)
        for friendly_name in ('value-focus', value_part):
            for suffix in ('-line', ''):
                self.carousel.add_stylable_classes(
                    keyval_parts.text_area,
                    friendly_name + suffix,
                )

    # ***

    def replace_val_container(
        self,
        val_container,
        keyval_widgets,
        set_focus=False,
    ):
        keyval_vsplit = self.details_container.get_children()[keyval_widgets.index]

        focus_state = set_focus and 'focus' or 'normal'

        # ***

        # Set classes on each part, title-normal-line, or title-focus-line.
        # Set also on inner text, title-normal or title-focus.
        # This clobbers default style that PPT uses on Label, 'class:label '.
        title_base_class = 'class:title-{}'.format(focus_state)
        title_line_class = '{}-line'.format(title_base_class)
        # Set classes more specific to the part type, e.g.,
        # title-[duration|start|end|activity|category|tags][-focus][-line].
        tpart_base_class = 'class:title-{}'.format(keyval_widgets.what_part)
        if set_focus:
            tpart_base_class += '-{}'.format(focus_state)  # += '-focus'
        tpart_line_class = '{}-line'.format(tpart_base_class)

        line_classes = '{} {} '.format(title_line_class, tpart_line_class)
        text_classes = '{} {} {} {} '.format(
            title_line_class, title_base_class, tpart_line_class, tpart_base_class,
        )

        keyval_vsplit.get_children()[0].style = line_classes
        title_widget = keyval_vsplit.get_children()[1]
        title_widget.style = text_classes
        keyval_vsplit.get_children()[2].style = line_classes

        # ***

        # On Label, to_container gets val_container.formatted_text_control.
        # On TextArea, to_container get val_container.window.
        value_widget = to_container(val_container)
        # Set class on value component, value-normal-line, or value-focus-line.
        value_line_class = 'class:value-{}-line '.format(focus_state)
        # Set class on value component, value-{part}[-focus]-line,
        # e.g., value-end-focus-line, or value-start-line.
        value_part_class = 'class:value-{}'.format(keyval_widgets.what_part)
        if set_focus:
            value_part_class += '-focus'
        value_part_class += '-line'
        # This clobbers default style that PPT use on TextArea, 'class:text-area '.
        value_widget.style = value_line_class + value_part_class
        keyval_vsplit.get_children()[3] = value_widget

        # ***

        self.add_stylable_classes(keyval_widgets, set_focus=set_focus)

    def replace_val_container_label(self, keyval_widgets):
        self.replace_val_container(
            keyval_widgets.val_label,
            keyval_widgets,
        )
        # keyval_widgets.val_label.window.style: 'class:value-normal-line'
        #   and formatted_text_control.style: ''
        #   and keyval_widgets.val_label.text
        #     is style tuples, [('class:value-normal', '...')...]
        keyval_widgets.val_label

    def replace_val_container_text_area(self, keyval_widgets):
        self.replace_val_container(
            keyval_widgets.text_area,
            keyval_widgets,
            set_focus=True,
        )

    # ***

    def edit_time_focus(self, keyval_widgets):
        self.active_widgets = keyval_widgets
        # Swap out a container in the layout.
        self.replace_val_container_text_area(keyval_widgets)
        # Focus the newly placed container.
        # MAYBE/2019-01-28: (lb): This is highly coupled, to say the least.
        #   Should maybe have zone_manager pass a focus callback.
        self.carousel.zone_manager.layout.focus(keyval_widgets.text_area)
        # Move the cursor to the end of the exit field,
        # e.g., if there's a date and time already set,
        # put the cursor after it all.
        self.send_cursor_right_to_end(keyval_widgets.text_area.buffer)
        # Wire a few simple bindings for editing (mostly rely on PPT's VI mode.)
        self.carousel.action_manager.wire_keys_edit_time()

    # ***

    def edit_time_leave(self, keyval_widgets):
        def _edit_time_leave():
            self.affirm(
                (self.active_widgets is None)
                or (keyval_widgets is self.active_widgets)
            )
            return apply_edited_and_refresh()

        def apply_edited_and_refresh():
            leave_okayed = not was_edited()
            if not leave_okayed:
                leave_okayed = self.edit_time_enter(passive=True)
            if not leave_okayed:
                return False
            return refresh_keyval()

        def was_edited():
            debug_log_text()
            return keyval_widgets.text_area.text != keyval_widgets.orig_val

        def debug_log_text():
            self.carousel.controller.client_logger.debug(
                'text_area.text: {} / orig_val: {}'.format(
                    keyval_widgets.text_area.text,
                    keyval_widgets.orig_val,
                )
            )

        def refresh_keyval():
            # Refresh labels now, so that old value isn't shown briefly and then
            # updated, which looks weird. Rather, update label first, then show.
            self.selectively_refresh()
            self.replace_val_container_label(self.active_widgets)
            self.active_widgets = None
            return True

        return _edit_time_leave()

    # ***

    def send_cursor_right_to_end(self, winbufr):
        end_posit = winbufr.document.get_end_of_document_position()
        # Generally same as: winbufr.document.get_end_of_line_position()
        winbufr.cursor_right(end_posit)

    # ***

    def edit_time_any_key(self, event=None):
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

    # FIXME/BACKLOG/2019-01-21: Notify user if time changed to not delete adjacent.
    #   - Test current behavior. Old hamster would delete facts if you extended one
    #     and showed others. I don't like that behavior! User can delete Facts first,
    #     and then fill in the empty time! (Or someone else can submit a PR so long
    #     as the destructive behavior is not the default.)
    #   - Probably use footer to show message; but could instead use popup modal.

    # FIXME/BACKLOG/2019-01-21: Need way to cancel after editing time:
    #   Possible key binding: Ctrl-q, ESC, q, etc.

    @catch_action_exception
    def edit_time_enter(self, event=None, passive=False):
        """"""
        leave_okayed = [True, ]

        def _edit_time_enter():
            edit_text = self.active_widgets.text_area.text
            # Note that carousel.edits_manager.curr_edit returns fact-under-edit
            # only if one already exists, but fact may be unedited, in which case
            # it'd return the original, unedited fact. So use the editable fact we
            # made earlier.
            edit_fact = self.zone_manager.facts_diff.edit_fact
            apply_edited_time(edit_fact, edit_text)
            return leave_okayed[0]

        def apply_edited_time(edit_fact, edit_text):
            self.carousel.controller.client_logger.debug(
                'edit_time_enter: edit_text: {}'.format(edit_text)
            )
            if not edit_text:
                apply_edit_time_removed(edit_fact)
            else:
                apply_edit_time_changed(edit_fact, edit_text)

        # ***

        def apply_edit_time_removed(edit_fact):
            if self.active_widgets is self.widgets_start:
                okay = self.apply_edit_time_removed_start(edit_fact, passive)
                if not okay:
                    # User hit 'enter'. Annoy them with a warning.
                    show_message_cannot_clear_start()
                # else, passive=True, and widget was reset to orig start
                # (because removing a Fact's start time is never allowed).
            else:
                self.affirm(self.active_widgets is self.widgets_end)
                okay = self.apply_edit_time_removed_end(edit_fact)
                if okay:
                    apply_edit_time_valid(edit_fact, edit_time=None)
                else:
                    # Always warn user, whether they hit 'enter' or are tabbing away.
                    show_message_cannot_clear_end()

        # ***

        def apply_edit_time_changed(edit_fact, edit_text):
            edit_time, parse_err = self.parse_dated(edit_text)
            if parse_err:
                show_message_cannot_parse_time(parse_err)
            else:
                apply_edit_time_valid(edit_fact, edit_time)

        def apply_edit_time_valid(edit_fact, edit_time):
            was_fact = edit_fact.copy()
            if self.active_widgets is self.widgets_start:
                was_time = edit_fact.start_fmt_local
                applied = self.apply_edit_time_start(
                    edit_fact, edit_time, verify_fact_times,
                )
            else:
                self.affirm(self.active_widgets is self.widgets_end)
                was_time = edit_fact.end_fmt_local_or_now
                applied = self.apply_edit_time_end(
                    edit_fact, edit_time, verify_fact_times,
                )
            check_conflicts_and_confirm(edit_fact, was_fact, was_time, applied)

        def verify_fact_times(edit_fact):
            # Check that edit_fact.start < edit_fact.end now, rather than
            # via apply_edit_time_start/apply_edit_time_end's call to
            # edits_manager.apply_edits. By doing it now, we will not have
            # to cleanup the undo stack, nor fix the current fact, nor any
            # neighbor fact.
            conflicts = must_complete_times(
                self.carousel.controller,
                new_facts=[edit_fact],
                progress=None,
                leave_blanks=True,
                other_edits={},
                suppress_barf=True,
            )
            if conflicts:
                edited_fact_alert_conflicts(conflicts)
                return False
            return True

        def check_conflicts_and_confirm(edit_fact, was_fact, was_time, applied):
            if not applied:
                # Nothing changed; no-op.
                return
            edited_fact_check_conflicts(edit_fact, was_fact, was_time)

        def edited_fact_check_conflicts(edit_fact, was_fact, was_time):
            # (lb): The application interface mostly precludes conflicts.
            #   The apply_edit_time_start/apply_edit_time_end methods do
            #   not allow conflicts with other Facts. But user can create a
            #   conflict with the Fact itself, e.g., by changing the end time
            #   to come before the start.
            conflicts = edited_fact_conflicts(edit_fact)
            if conflicts:
                edited_fact_alert_conflicts(conflicts)
                edited_fact_cleanup_rejected(edit_fact, was_fact, was_time)

        def edited_fact_alert_conflicts(conflicts):
            self.affirm(len(conflicts) == 1)
            conflict_msg = conflicts[0][2]
            show_message_conflicts_found(conflict_msg)

        def edited_fact_cleanup_rejected(edit_fact, was_fact, was_time):
            # Toss the rejected edit from the undo stack.
            undone = self.carousel.edits_manager.toss_last_edit()
            self.affirm(undone)
            # Reset the Fact, otherwise the edit will stick!
            #   # Won't work! Screws up prev/next links, and leaves undo!:
            #   edit_fact.start = was_fact.start
            #   edit_fact.end = was_fact.end
            # MAYBE/2020-04-09: (lb): Pretty sure we're missing code to
            # reset the fact. (This code path used to be taken when a fact
            # end time < its start time. But that case is now handled earlier,
            # and the flow won't make it here. And if you set a fact's start
            # time earlier than the previous fact start time, it'll be auto-
            # corrected. So I'm not quite sure what use case triggers this
            # branch anymore!)
            self.affirm(edit_fact.start == was_fact.start)
            self.affirm(edit_fact.end == was_fact.end)
            # FIXME/2020-04-09: (lb): Seriously, what gets you here?
            # - Document what use case gets you here if/when this fires.
            self.affirm(False)
            # Update the control text.
            self.active_widgets.text_area.text = was_time

        def edited_fact_conflicts(edit_fact):
            # Skip all unstored, edited Facts.
            other_edits = {
                fact.pk: fact for fact in self.carousel.edits_manager.prepared_facts
            }

            conflicts = must_complete_times(
                self.carousel.controller,
                new_facts=[edit_fact],
                progress=None,
                leave_blanks=True,
                other_edits=other_edits,
                suppress_barf=True,
            )
            self.carousel.controller.client_logger.debug(
                'no. conflicts found: {}'.format(len(conflicts))
            )
            return conflicts

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
                _('Drat!'),
                edit_text,
            )

        def show_message_conflicts_found(conflict_msg):
            show_message_and_deny_leave(
                self.carousel.zone_manager.root,
                _('Not so fast!'),
                conflict_msg,
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

        return _edit_time_enter()

    # ***

    def parse_dated(self, edit_text):
        def _parse_dated():
            time_now = self.carousel.controller.now
            parseable = prepare_dated()
            try:
                edit_time = parse_dated(parseable, time_now, cruftless=True)
            except ParserInvalidDatetimeException as err:
                # E.g., try entering date "2019-01-27 18."
                edit_time = None
                parse_err = str(err)
            else:
                self.affirm(isinstance(edit_time, datetime))
                parse_err = None
            return edit_time, parse_err

        def prepare_dated():
            # Per date_separators, we let user specify which optional
            # separators they'd like to, but iso8601 only allows dashes to
            # separate the year parts; a space, 't', or 'T' to distinguish
            # the year from the time; and colons to separate clock time's
            # hours from minutes. Here we remove all those non-numeric
            # characters and just build the iso8601-worthy string ourselves.
            # We also allow incomplete YYYYMM (iso8601 only allows YYYY-MM
            # or YYYYMMDD), as well as incomplete time (say, '12', for noon).
            numberless = re.sub(r'[^\d]+', '', edit_text)
            # (lb): Alright, maybe this parsing should be pushed down to parse_dated.
            # - Add punctuation based on number of digits, i.e.,
            #   YYYY 4 | YYYYMM 6 | YYYYMMDD 8 | YYYYMMDDhh 10 | YYYYMMDDhhmm 12
            # - Note that clock time still works, e.g., `1000` will be interpreted
            #   as 10 AM. And `100` as 1 AM.
            pattern = r''
            replace = r''
            n_digits = len(numberless)
            if n_digits >= 4:
                pattern += r'(....)'
                replace += r'\1'
            if n_digits >= 6:
                pattern += r'(..)'
                replace += r'-\2'
            if n_digits >= 8:
                pattern += r'(..)'
                replace += r'-\3'
            if n_digits >= 10:
                pattern += r'(..)'
                replace += r' \4'
            if n_digits >= 12:
                pattern += r'(..)'
                replace += r':\5'
            reformatted = re.sub(pattern, replace, numberless)
            self.carousel.controller.client_logger.debug(
                'reformatted: {}'.format(reformatted)
            )
            return reformatted

        return _parse_dated()

    # ***

    @catch_action_exception
    # SKIP: @ZoneContent.Decorators.reset_showing_help
    def toggle_focus_description(self, event):
        self.zone_manager.toggle_focus_time_widget(self.zone_manager.content_control)

    # ***

    @catch_action_exception
    def undo_command(self, event):
        # FIXME/2019-01-21: Is this correct? Use case:
        #   - Press 'e'; edit 'end'; press Enter to apply change.
        #   - Press 'e' again; edit 'end'; press Ctrl-z.
        #   - Expect: previous (intermediate) end time, not original end time!
        #   - For original end time: press 'R' reset!
        orig_fact = self.zone_manager.facts_diff.orig_fact
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

