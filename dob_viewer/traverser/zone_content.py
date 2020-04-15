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

"""Facts Carousel "Matter" (Fact Description) / Content area"""

from functools import update_wrapper

from prompt_toolkit.filters import Always, Never
from prompt_toolkit.widgets import Frame, TextArea

from .exceptions import catch_action_exception
from .zone_helpful import NUM_HELP_PAGES, render_carousel_help

__all__ = (
    'ZoneContent',
)


class ZoneContent(object):
    """"""
    def __init__(self, carousel):
        self.carousel = carousel
        self.showing_help = 0
        # For your convenience, attributes to eliminate one object hop.
        self.content_lexer = self.carousel.content_lexer
        self.classes_style = self.carousel.classes_style

    # ***

    def on_reset_hide_help(self):
        was_showing = self.showing_help
        self.showing_help = 0
        return was_showing != 0

    class Decorators(object):
        @classmethod
        def reset_showing_help(cls, func):
            def wrapper(obj, event, *args, **kwargs):
                # This won't redraw because we don't call rebuild_viewable.
                # So, if, e.g., user is on first Fact and clicks Left, the
                # Help will not go away, because decrement() won't refresh.
                obj.carousel.zone_manager.zone_content.on_reset_hide_help()
                obj.carousel.zone_manager.zone_lowdown.update_status(hot_notif='')
                func(obj, event, *args, **kwargs)

            return update_wrapper(wrapper, func)

    # ***

    def standup(self):
        self.scrollable_height = self.classes_style['content-height']
        self.scrollable_width = self.classes_style['content-width']
        self.enable_wrapping = self.classes_style['content-wrap']
        self.setup_scrollable()

    # ***

    def setup_scrollable(self):
        """"""
        def _setup_scrollable():
            self.content_width = calculate_width()
            self.content = content_text_area(self.content_width)
            self.scrollable_frame = Frame(
                self.content,
                # title="Fact Description",
                style='class:content-fact',
            )

            if self.content_lexer is not None:
                self.content_lexer.content_width = self.content_width

        def calculate_width():
            avail_width = self.carousel.avail_width
            if not self.scrollable_width:
                return avail_width
            return restricted_width(avail_width)

        def restricted_width(avail_width):
            formatted = self.carousel.zone_manager.zone_lowdown.format_lowdown_text()
            len_footer = sum([len(part[1]) for part in formatted])
            content_width = max(avail_width, len_footer)
            # (lb): The width excludes the border columns, so the content
            # area will actually be two columns wider. Here we subtract
            # 1 of those columns from the width, so that the footer text
            # right-aligns one column less than the description content
            # (we could subtract 2, but then the footer is flush with the
            # border column, which I do not find as visually appealing).
            content_width -= 1
            return content_width

        # FIXME/BACKLOG/2019-01-21: Another old comment:
        #   Make `lexer` style option... or config option.

        def content_text_area(content_width):
            # Layout for displaying Fact description.
            # The Frame creates the border.
            text_area = TextArea(
                text='',
                read_only=True,
                focusable=True,  # Unnecessary; included for completeness.
                width=content_width,
                # There's also:
                #   dont_extend_width=True,
                height=self.scrollable_height,
                # Scrollbar looks wonky.
                #  And it's vertical, not horizontal,
                #   even when wrap_lines=False.
                #  scrollbar=True,
                # (lb): If user wanted to have horizontal scrolling,
                # you can set wrap_lines=False so the long lines are
                # not wrapped at width, but I cannot determine how to
                # scroll right in the TextArea. There's probably a way,
                # I'm guessing. But not a feature I care much about.
                #  wrap_lines=False,
                lexer=self.content_lexer,
            )
            return text_area

        _setup_scrollable()

    # ***

    def selectively_refresh(self):
        self.rebuild_viewable()

    # ***

    def focus_content(self, focus):
        if focus:
            self.enter_content()
        # else: nothing to do on leave.
        return True

    def enter_content(self):
        self.carousel.zone_manager.layout.focus(self.content)
        self.carousel.action_manager.wire_keys_normal()

    # *** API

    @catch_action_exception
    def cursor_up_one(self, event):
        """"""
        count = self.carousel.update_handler.apply_count_multiplier()
        self.content.buffer.cursor_up(count=count)

    @catch_action_exception
    def cursor_down_one(self, event):
        """"""
        count = self.carousel.update_handler.apply_count_multiplier()
        self.content.buffer.cursor_down(count=count)

    @catch_action_exception
    def scroll_down(self, event):
        """"""
        view_height = self.view_height()
        self.content.buffer.cursor_down(view_height)
        self.reset_cursor_left_column()

    def view_height(self):
        view_height = self.scrollable_height - 1
        if self.content.buffer.document.cursor_position_row == 0:
            # If cursor is at home posit, first page down moves cursor
            # to bottom of view. So scroll additional page, otherwise
            # user would have to press PageDown twice to see more text.
            view_height *= 2
        self.carousel.controller.client_logger.debug(
            'view_height: {}'.format(view_height)
        )
        return view_height

    @catch_action_exception
    def scroll_up(self, event):
        """"""
        self.content.buffer.cursor_up(self.scrollable_height - 1)
        self.reset_cursor_left_column()

    @catch_action_exception
    def scroll_top(self, event):
        """"""
        self.content.buffer.cursor_position = 0

    @catch_action_exception
    def scroll_bottom(self, event):
        """"""
        self.content.buffer.cursor_position = len(self.content.buffer.text)
        self.reset_cursor_left_column()

    # ***

    def reset_cursor_left_column(self):
        self.content.buffer.cursor_left(
            # PPT returns a relative distance, e.g., -7, or 0 if already there.
            # A similar command, get_cursor_left_position(), return -1 or 0.
            -self.content.buffer.document.get_start_of_line_position()
        )

    # ***

    def rebuild_viewable(self):
        content_text = self.apply_scrollable_style()
        self.content.buffer.read_only = Never()
        self.content.buffer.text = content_text
        self.content.buffer.read_only = Always()
        return self.scrollable_frame.container

    def apply_scrollable_style(self):
        if self.showing_help:
            return self.apply_scrollable_style_help()
        else:
            return self.apply_scrollable_style_fact()

    def apply_scrollable_style_help(self):
        self.scrollable_frame.container.style = 'class:content-help'
        # MAYBE: (lb): It is easy to format a PPT Frame's content?
        #   (I tried passing HTML(CAROUSEL_HELP) but, uh, nope.)
        #   (This is not too important; I thought it might be nice
        #   (polishing feature) to beautify the help (even more).)
        return render_carousel_help()

    def apply_scrollable_style_fact(self):
        self.scrollable_frame.container.style = 'class:content-fact'

        curr_edit = self.carousel.edits_manager.curr_edit

        # BACKLOG: Fact InterVal GaP Interval
        # MAYBE: Don't color after edited/added?
        #        Or probably 'unsaved-fact' style will override.
        if curr_edit.is_gap:
            self.scrollable_frame.container.style += ' class:interval-gap'

        # MAYBE: Just go through dirty_reasons and add as classes...
        if 'unsaved-fact' in curr_edit.dirty_reasons:
            self.scrollable_frame.container.style += ' class:unsaved-fact'

        # (lb): So, what do we call the stylable thing we let the user style?
        # The static style is currently 'content-fact'. The text in the content
        # area being styled is the fact description, as well as the box lines
        # around it that PPT draws. The word "description" is a lot to type,
        # e.g., "fact-description", and most users probably know what "content"
        # is, so we could call it "content-fact"... or "body" is pretty familiar,
        # though the word "body" feels like a harbinger of HTML, or at least Clue.
        # (I also considered just "content" but I like the common "fact-" prefix.)
        self.carousel.add_stylable_classes(
            self.scrollable_frame.container,
            'content-fact',
            fact=curr_edit,
        )

        content_text = curr_edit.description or ''

        content_text = self.wrap_on_whitespace_maybe(content_text)

        return content_text

    def wrap_on_whitespace_maybe(self, content_text):
        # FIXME/BACKLOG/2019-01-21: Old comment:
        #   Make KeyBinding for toggling wrapping.
        #        Ideally, 3 options: wrap, no wrap, scrollbar.
        #          For now, wrap and no-wrap,
        #            (lb): b/c I do not know if horizontal scrollbar is easily doable.
        if not self.enable_wrapping:
            return content_text
        lines_wrapped = ''
        for line in content_text.splitlines():
            line_wrapped = ''
            while len(line) > 0:
                if len(line) > self.content_width:
                    space_idx = line.rfind(' ', 0, self.content_width)
                    space_idx = self.content_width if space_idx < 1 else space_idx
                    line_piece = line[:space_idx]
                    space_idx += 1  # Do not write space at beginning of next line,
                    line = line[space_idx:]
                else:
                    line_piece = line
                    line = ''
                line_wrapped += "\n" if line_wrapped else ''
                line_wrapped += line_piece
            lines_wrapped += line_wrapped + "\n"
        return lines_wrapped

    # ***

    @catch_action_exception
    def rotate_help(self, event):
        assert NUM_HELP_PAGES == 2  # Otherwise, we need to update this logic:
        self.showing_help = (self.showing_help + 1) % (NUM_HELP_PAGES + 1)
        if self.showing_help == 1:
            self.scroll_top(event)
        elif self.showing_help == 2:
            self.scroll_bottom(event)
        else:
            self.scroll_top(event)
        self.rebuild_viewable()

