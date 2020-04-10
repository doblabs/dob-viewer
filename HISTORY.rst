#######
History
#######

.. |dob| replace:: ``dob``
.. _dob: https://github.com/hotoffthehamster/dob

.. |dob-prompt| replace:: ``dob-prompt``
.. _dob-prompt: https://github.com/hotoffthehamster/dob-prompt

.. |dob-viewer| replace:: ``dob-viewer``
.. _dob-viewer: https://github.com/hotoffthehamster/dob-viewer

.. :changelog:

1.0.5 (2020-04-09)
==================

- Bugfix: If you edit end to be before start, dob crashes after alert dialog.

- Improve: On neighbor time adjust, prefer fact_min_delta for min. time width.

1.0.4 (2020-04-08)
==================

- Bugfix: Changing focus breaks on Ctrl-S from time widget.

- Bugfix: Upstream PTK asynio upgrade breaks popup dialog.

  Aka, convert generator-based coroutines to async/await syntax.

- Bugfix: User unable to specify editor.lexer.

- Bugfix: Footer component class style (re)appended every tick.

1.0.3 (2020-04-01)
==================

- Bugfix: Send package name to get_version, lest nark use its own.

1.0.2 (2020-04-01)
==================

- Docs: Remove unnecessary version details from carousel help.

- Refactor: DRY: Use new library get_version.

1.0.1 (2020-03-31)
==================

- Bugfix: Repair demo command (fix class-name formation from tags containing spaces).

1.0.0 (2020-03-30)
==================

- Booyeah: Inaugural release (spin-off from dob).

