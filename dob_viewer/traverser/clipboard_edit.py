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

"""Fact-editing “Clipboard” manager."""

from gettext import gettext as _

__all__ = (
    'ClipboardEdit',
)


class ClipboardEdit(object):
    """"""
    def __init__(self, edits_manager):
        self.controller = edits_manager.controller
        self.redo_undo = edits_manager.redo_undo
        self._clipboard = {}
        self.reset_paste()

    @property
    def clipboard(self):
        return self._clipboard

    @clipboard.setter
    def clipboard(self, clipboard):
        if self._clipboard != clipboard:
            self.paste_cnt = None
        self._clipboard = clipboard

    def reset_paste(self):
        self.paste_cnt = None

    # ***

    def copy_activity(self, curr_edit):
        self.clipboard = {'activity': curr_edit.activity, }

    def copy_tags(self, curr_edit):
        self.clipboard = {'tags': curr_edit.tags, }

    def copy_description(self, curr_edit):
        self.clipboard = {'description': curr_edit.description, }

    def copy_fact(self, curr_edit):
        self.clipboard = {'fact': curr_edit.copy(), }

    # ***

    def paste_copied_meta(self, edit_fact, reset_fact):
        """"""
        def _paste_copied_meta(edit_fact):
            if not self.clipboard:
                return None
            self.controller.affirm(len(self.clipboard) == 1)
            for paste_what, paste_val in self.clipboard.items():
                pasted_what = paste_copied_what(edit_fact, paste_what, paste_val)
            return pasted_what

        def paste_copied_what(edit_fact, paste_what, paste_val):
            if paste_what == 'activity':
                edit_fact.activity = paste_val
                pasted_what = _('activity')
            elif paste_what == 'tags':
                edit_fact.tags = paste_val
                pasted_what = _('tags')
            elif paste_what == 'description':
                edit_fact.description = paste_val
                pasted_what = _('description')
            else:
                self.controller.affirm(paste_what == 'fact')
                # MAYBE: Add a paste-all meta option? Or is cycle-pasting ok?
                #  edit_fact.activity = paste_val.activity
                #  edit_fact.tags = paste_val.tags
                #  edit_fact.description = paste_val.description
                pasted_what = paste_copied_fact(edit_fact, paste_val)
            return pasted_what

        def paste_copied_fact(edit_fact, paste_val):
            restore_fact_pre_paste(edit_fact)
            self.paste_cnt = paste_cnt_increment(edit_fact, paste_val)
            if self.paste_cnt == 0:
                edit_fact.activity = paste_val.activity
                edit_fact.tags = paste_val.tags
                pasted_what = _('activity and tags')
            elif self.paste_cnt == 1:
                edit_fact.activity = paste_val.activity
                pasted_what = _('activity')
            elif self.paste_cnt == 2:
                edit_fact.tags = paste_val.tags
                pasted_what = _('tags')
            else:
                self.controller.affirm(self.paste_cnt == 3)
                edit_fact.activity = paste_val.activity
                edit_fact.tags = paste_val.tags
                edit_fact.description = paste_val.description
                pasted_what = _('activity, tags, and description')
            return pasted_what

        def restore_fact_pre_paste(edit_fact):
            if self.paste_cnt is None:
                return
            reset_fact(edit_fact)

        def paste_cnt_increment(edit_fact, paste_val):
            paste_cnt = None
            if self.paste_cnt == 3:
                self.paste_cnt = None
            if paste_cnt is None and self.paste_cnt is None:
                if (
                    edit_fact.activity == paste_val.activity
                    and edit_fact.tags == paste_val.tags
                ):
                    self.paste_cnt = 0
                else:
                    paste_cnt = 0
            if paste_cnt is None and self.paste_cnt == 0:
                if edit_fact.activity == paste_val.activity:
                    self.paste_cnt = 1
                else:
                    paste_cnt = 1
            if paste_cnt is None and self.paste_cnt == 1:
                if edit_fact.tags == paste_val.tags:
                    self.paste_cnt = 2
                else:
                    paste_cnt = 2
            if paste_cnt is None:
                self.controller.affirm(self.paste_cnt == 2)
                paste_cnt = 3
            return paste_cnt

        return _paste_copied_meta(edit_fact)

