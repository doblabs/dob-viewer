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
"""~/.config/dob/styling/stylit.conf definition and encapsulating class."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

from nark.config.inify import section
from nark.config.subscriptable import Subscriptable

__all__ = (
    'create_stylit_object',
)


def create_stylit_object():

    COMPONENTRY_CLASSIFIER_HELP = _(
        "String to append to component, e.g., 'class:my-class1 class:my-class2'."
    )

    @section(None)
    class StylitRoot(object):

        def __init__(self):
            pass

    # ***

    @StylitRoot.section(None)
    class StylitRuleset(Subscriptable):
        """"""

        def __init__(self):
            pass

        # ***

        @property
        @StylitRoot.setting(
            _("If True, skip this ruleset."),
        )
        def disabled(self):
            return False

        # ***

        @property
        @StylitRoot.setting(
            _("ADVANCED: Optional code to run in context of rules evaluator."),
        )
        def eval(self):
            # E.g.,
            #   eval = fact.category_name == 'My Category'
            return ''

        @property
        @StylitRoot.setting(
            _("Generated value."),
            name='__eval__',
            hidden=True,
            # Not necessary, because we generate the value, but could say:
            #   validate=inspect.iscode,
        )
        def compiled_eval(self):
            return None

        # ***

        @property
        @StylitRoot.setting(
            _("Match Facts with the specified Activity name."),
        )
        def activity(self):
            return ''

        # ---

        @property
        @StylitRoot.setting(
            _("Match Facts with specified comma-separated list of Activities."),
        )
        def activities(self):
            return []

        # ***

        @property
        @StylitRoot.setting(
            _("Match Facts with the specified Category name."),
        )
        def category(self):
            return ''

        # ---

        @property
        @StylitRoot.setting(
            _("Match Facts with specified comma-separated list of Categories."),
        )
        def categories(self):
            return []

        # ***

        @property
        @StylitRoot.setting(
            _("Match Facts with the specified Tag."),
        )
        def tag(self):
            return ''

        # ---

        @property
        @StylitRoot.setting(
            _("Match Facts with any of the matching tags."),
        )
        def tags(self):
            return []

        # ...

        @property
        @StylitRoot.setting(
            _("Match Facts with any of the matching tags."),
            name='tags-any',
        )
        def tags_any(self):
            return []

        # (lb): I'm indecisive. tags-any, or tags-or, or both??
        # - We can just 'hidden' one of them, and still let users decide.
        @property
        @StylitRoot.setting(
            _("Match Facts with any of the matching tags."),
            name='tags-or',
            hidden=True,
        )
        def tags_or(self):
            return []

        # ...

        @property
        @StylitRoot.setting(
            _("Match Facts with *all* of the matching tags."),
            name='tags-all',
        )
        def tags_all(self):
            return []

        # (lb): I'm indecisive. tags-all, or tags-and, or both??
        # - We can just 'hidden' one of them, and still let users decide.
        @property
        @StylitRoot.setting(
            _("Match Facts with *all* of the matching tags."),
            name='tags-and',
            hidden=True,
        )
        def tags_and(self):
            return []

        # ***

        # FEATURE-REQUEST/2019-12-02: (lb): Additional conditionals for time attrs,
        # start/end/duration, except this could get more complicated than the above,
        # e.g., imagine `fact-duration-le = 10` for any fact with duration < 10 minutes.
        # - Currently, you can still condition from the fact start/end/duration
        #   using the 'eval' setting, Where anything goes!

    # ***

    @StylitRoot.section(None)
    class StylitClassify(Subscriptable):
        """"""

        def __init__(self):
            pass

        # ***
        # ***

        # (lb): I feel like I should DRY this up.
        # But also this makes it pretty clear what's happening.

        # ***
        # *** APPLICATION STREAMER
        # ***

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='header-streamer',
        )
        def header_streamer(self):
            return ''

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='header-streamer-line',
        )
        def header_streamer_line(self):
            return ''

        # ***
        # *** HEADER META LINES -- TITLES HALF (LEFT SIDE)
        # ***

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-duration',
        )
        def header_title_duration(self):
            return ''

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-duration-line',
        )
        def header_title_duration_line(self):
            return ''

        # ***

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-start',
        )
        def header_title_start(self):
            return ''

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-start-line',
        )
        def header_title_start_line(self):
            return ''

        # ***

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-end',
        )
        def header_title_end(self):
            return ''

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-end-line',
        )
        def header_title_end_line(self):
            return ''

        # ***

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-activity',
        )
        def header_title_activity(self):
            return ''

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-activity-line',
        )
        def header_title_activity_line(self):
            return ''

        # ***

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-category',
        )
        def header_title_category(self):
            return ''

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-category-line',
        )
        def header_title_category_line(self):
            return ''

        # ***

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-tags',
        )
        def header_title_tags(self):
            return ''

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='title-tags-line',
        )
        def header_title_tags_line(self):
            return ''

        # ***
        # *** HEADER META LINES -- VALUES HALF (RIGHT SIDE)
        # ***

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-duration',
        )
        def header_fact_duration(self):
            return ''

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-duration-line',
        )
        def header_fact_duration_line(self):
            return ''

        # ***

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-start',
        )
        def header_fact_start(self):
            return ''

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-start-line',
        )
        def header_fact_start_line(self):
            return ''

        # ***

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-end',
        )
        def header_fact_end(self):
            return ''

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-end-line',
        )
        def header_fact_end_line(self):
            return ''

        # ***

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-activity',
        )
        def header_fact_activity(self):
            return ''

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-activity-line',
        )
        def header_fact_activity_line(self):
            return ''

        # ***

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-category',
        )
        def header_fact_category(self):
            return ''

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-category-line',
        )
        def header_fact_category_line(self):
            return ''

        # ***

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-tags',
        )
        def header_fact_tags(self):
            return ''

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='value-tags-line',
        )
        def header_fact_tags_line(self):
            return ''

        # ***
        # *** CONTENT AREA CONDITIONAL STYLIT
        # ***

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='fact-content',
        )
        def scrollable_frame(self):
            return ''

        # ***
        # *** FACT ID CONDITIONAL STYLIT (LOWER LEFT CORNER)
        # ***

        @property
        @StylitRoot.setting(
            COMPONENTRY_CLASSIFIER_HELP,
            name='fact-id',
        )
        def fact_id(self):
            return ''

        # ***
        # ***

    return StylitRoot

