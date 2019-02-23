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
""""""

from __future__ import absolute_import, unicode_literals

from prompt_toolkit.lexers import Lexer

__all__ = (
    'rainbow',
)


class BaseLexer(Lexer):
    """"""
    def __init__(self):
        self._content_width = None

    @property
    def content_width(self):
        return self._content_width

    @content_width.setter
    def content_width(self, content_width):
        self._content_width = content_width


def truncater():
    class TruncatingLexer(BaseLexer):
        @BaseLexer.content_width.setter
        def content_width(self, content_width):
            self._content_width = content_width
            self.dots_cnt = 3
            self.trunc_at = max(self.content_width - self.dots_cnt, 0)

        def lex_document(self, document):
            def get_line(lineno):
                line = document.lines[lineno]
                if self.content_width:
                    if len(line) > self.content_width:
                        line = line[:self.trunc_at]
                        line += '━' * self.dots_cnt
                return [("#00ff55", c) for c in line]

            return get_line

    return TruncatingLexer


def rainbow():
    from prompt_toolkit.styles.named_colors import NAMED_COLORS

    class RainbowLexer(BaseLexer):
        def lex_document(self, document):
            colors = list(sorted(NAMED_COLORS, key=NAMED_COLORS.get))

            def get_line(lineno):
                return [
                    (colors[i % len(colors)], c)
                    for i, c in enumerate(document.lines[lineno])
                ]

            return get_line

    return RainbowLexer

