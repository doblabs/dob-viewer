############
Installation
############

.. |dob-viewer| replace:: ``dob-viewer``
.. _dob-viewer: https://github.com/hotoffthehamster/dob-viewer

.. |virtualenv| replace:: ``virtualenv``
.. _virtualenv: https://virtualenv.pypa.io/en/latest/

.. |workon| replace:: ``workon``
.. _workon: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html?highlight=workon#workon

To install system-wide, run as superuser:

.. code-block:: sh

   $ pip3 install dob-viewer

To install user-local, simply run:

.. code-block:: sh

    $ pip3 install -U dob-viewer

To install within a |virtualenv|_, try:

.. code-block:: sh

    $ mkvirtualenv dob-viewer
    (dob-viewer) $ pip3 install dob-viewer

To develop on the project, link to the source files instead:

.. code-block:: sh

    (dob-viewer) $ deactivate
    $ rmvirtualenv dob-viewer
    $ git clone git@github.com:hotoffthehamster/dob-viewer.git
    $ cd dob-viewer
    $ mkvirtualenv -a $(pwd) --python=/usr/bin/python3.6 dob-viewer
    (dob-viewer) $ make develop

After creating the virtual environment,
to start developing from a fresh terminal, run |workon|_:

.. code-block:: sh

    $ workon dob-viewer
    (dob-viewer) $ ...

