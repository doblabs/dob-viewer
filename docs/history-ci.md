# History

[comment]: # DEV: release-ghub-pypi scrapes Markdown from the first section below for the GitHub release.

## 1.0.7 (2020-04-12)

- Feature: Make all key bindings user configurable.

  - Run `dob config dump editor-keys` to see all the mappings.

  - User can specify zero, one, or multiple keys for each action.

- Improve: Remove 'escape'-only binding to avoid exit on unmapped Ctrl-keys.

- Bugfix: Catch Ctrl-C on dirty-quit confirmation, to avoid unseemly stack trace.

- Bugfix: Ctrl-W not saving on exit.

- Improve: Remove the Ctrl-W save-and-exit key binding.

  - Convention is that Ctrl-W is "close", but what would that be in dob?

  - The command remains but the binding was removed. The user can assign
    a key binding in their config if they want to enable this command.

- Feature: Vim-like command mode (lite).

  - Just the three commands, `:w`, `:q`, and `:wq`.

  - Because dob uses EDITOR, if Vim is user's editor, user could
    run `:wq` twice in a row to save their Fact description, leave
    the Vim editor, and then save and quit dob.

- Feature: +/-N time adjustment commands.

  - Type minus to begin a start time adjustment command. E.g., if you
    want to set the start time to ten minutes before the end time, type
    `-10<CR>`. Or type `-10m` (for minutes). For the active Fact, the
    time is calculated relative to "now".

  - Type a plus to begin an end time adjustment command, followed by
    an integer or floating point number, and then press Enter or "m"
    for minutes, or "h" for hours.

    - E.g., to set the end time 2.5 hours after the start time, type `+2.5h`.

- Feature: Add modifier key (defaults to `!`) to allow interval gap.

  - E.g., consider the  command `-1h`, which sets start 1 hour before end.
    If it makes the current Fact's time shorter, then it stretches the
    previous Fact's end time, as well.

    - To not touch the neighbor Fact but to leave a gap instead,
      press the modifier key after entering the number, e.g., `-1!h`.

  - User can change the modifier key via the `editor-keys.allow_time_gap`
    config setting.

- Feature: Convenient 1- and 5-minute single-key time nudging commands.

  - E.g., `[` and `]` to decrement or increment end by 1 min., or
    add shift press for 5 mins., i.e., `{` and `}`.

  - Likewise, use `,` and `.` to nudge start time
    backwards or forwards by 1 minute, respectively;
    and use `<` and `>` for five minutes instead.

  - All four keys are user-customizable, of course!

- Bugfix: Ensure Facts marked dirty after time nudging.

  - Or user is not asked to save on exit after nudging time.

- Bugfix: Long press time nudge is not increasing deltas over time.

  - E.g., if user holds Ctrl-left down, it starts adjusting the time by
    one minute for each press generated, but it was not increasing to
    five minutes per press, etc., the longer the user kept the key pressed.

- Improve: Ensure neighbor Fact time width not squashed to 0.

- Bugfix: Cannot jump to first/final fact if current Fact within jump delta.

  - E.g., Consider user is on current Fact, 2020-04-12 12:00 to 13:00, and
    the final Fact is from 2020-04-12 15:00 to 16:00. Pressing `K` does not
    jump to the final Fact, because it was less than 1 day ahead of current.

- Improve: On jump day from active Fact, use now as reference time.

  - This feels more natural, rather than jumping from the start of the
    active Fact, and prevents jumping back more than a day.

- Feature: Add Vim-like [count] prefix to Jump and Nudge commands.

  - E.g., user has been able to press `j` to go to the previous Fact.
    Now they can press `5j` to go back 5 Facts.

  - Likewise for jumping by day, e.g., `2.5K` will jump forward 2.5 days.

  - Same for time nudging, `Ctrl-left` has been used for decrementing the
    end time by 1 minute. Now user can specify exact amount, e.g., to
    decrease the end time by 4.2 minutes, the user can type `4.2<Ctrl-left>`.

  - User can type `!` before or after digits to signal that a time nudge
    command should leave a gap rather than stretching a neighbor's time,
    e.g., `!1<Ctrl-right>` and `1!<Ctrl-right>` are equivalent.

  - To give user better visibility into what's happening, the jump commands
    now print a status message indicating how many days or number of Facts
    were jumped. When jumping by day, the time reference used is also shown,
    which is helpful if there's a long Fact or Gap, so the user does not get
    confused when their jump does not appear to do anything (i.e., when
    time reference changes but locates the same Fact that was showing).

## 1.0.6 (2020-04-10)

- Enhance: Let user clear end time of final Fact.

## 1.0.5 (2020-04-09)

- Bugfix: If you edit end to be before start, dob crashes after alert dialog.

- Improve: On neighbor time adjust, prefer fact_min_delta for min. time width.

## 1.0.4 (2020-04-08)

- Bugfix: Changing focus breaks on Ctrl-S from time widget.

- Bugfix: Upstream PTK asynio upgrade breaks popup dialog.

  Aka, convert generator-based coroutines to async/await syntax.

- Bugfix: User unable to specify editor.lexer.

- Bugfix: Footer component class style (re)appended every tick.

## 1.0.3 (2020-04-01)

- Bugfix: Send package name to get_version, lest nark use its own.

## 1.0.2 (2020-04-01)

- Docs: Remove unnecessary version details from carousel help.

- Refactor: DRY Use new library get_version.

## 1.0.1 (2020-03-31)

- Bugfix: Repair demo command (fix class-name formation from tags containing spaces).

## 1.0.0 (2020-03-30)

- Booyeah: Inaugural release (spin-off from dob).

