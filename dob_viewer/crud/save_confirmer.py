# This file exists within 'dob-viewer':
#
#   https://github.com/hotoffthehamster/dob-viewer
#
# Copyright © 2018-2020 Landon Bouma. All rights reserved.
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

from ..config.styling.classes_style import (
    load_classes_style,
    load_matches_style
)
from ..config.styling.content_lexer import load_content_lexer
from ..config.styling.no_completion import load_no_completion


__all__ = (
    'prompt_and_save_confirmer',
)


# ***

def prompt_and_save_confirmer(
    controller,
    edit_facts=None,
    orig_facts=None,
    backup_callback=None,
    dry=False,
    **kwargs,
):
    """"""

    classes_style = load_classes_style(controller)
    matches_style = load_matches_style(controller)
    content_lexer = load_content_lexer(controller)
    no_completion = load_no_completion(controller)

    # Lazy-load the carousel and save ~0.065s.
    from dob_viewer.traverser.carousel import Carousel

    carousel = Carousel(
        controller,
        edit_facts=edit_facts,
        orig_facts=orig_facts,
        dirty_callback=backup_callback,
        dry=dry,
        classes_style=classes_style,
        matches_style=matches_style,
        content_lexer=content_lexer,
        no_completion=no_completion,
    )

    ready_facts = carousel.gallop(**kwargs)

    # The Carousel forces the user to save to exit! So ready_facts is empty!!
    # Or the user quit without saving, which would also mean no ready facts.
    # - 2020-01-28: (lb): If I recall correctly, I had originally
    #   plumbed Carousel to have you *review* Facts being imported
    #   (and only those Facts; user did not see other Facts); but now
    #   user sees Carousel of all Facts, with imported Facts inserted,
    #   but not saved, and user saves through Carousel.
    #   - Which is fine, probably desirable. But because user might
    #     have insisted `not use_carousel`, this module still has
    #     code to save Facts independent of the Carousel.
    #     Nonetheless, the Carousel is still coded to return a Facts
    #     array...
    #     MAYBE/2020-01-28: Could probably remove gallop() return list,
    #                  I think nowadays it'll always be the empty list??
    controller.affirm(not ready_facts)

    # CLOSED_LOOP: (lb): whoa_nellie is (disabled) kludge to avoid abandoned
    # event loop RuntimeError (better solution is needed; but sleeping here
    # before app exit can anecdotally avoid issue. And by "anecdotal" I mean
    # not necessarily guaranteed, so not a proper solution (and not even a
    # proper "kludge" by more stringent standards)).
    # TESTME/2020-02-01: Is this still necessary? Especially in PTK3?
    carousel.whoa_nellie()

    # ***
