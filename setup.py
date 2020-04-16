# This file exists within 'dob-viewer':
#
#   https://github.com/hotoffthehamster/dob-viewer

"""
Packaging instruction for setup tools.

Refs:

  https://setuptools.readthedocs.io/

  https://packaging.python.org/en/latest/distributing.html

  https://github.com/pypa/sampleproject
"""

from setuptools import find_packages, setup

# *** Package requirements.

requirements = [
    # The best optparser of any language, tops.
    #  https://github.com/pallets/click
    #    'click',
    # Because too busy developing our own code, our fork!
    #  https://github.com/hotoffthehamster/click
    'click-hotoffthehamster >= 7.1.1, < 8',
    # INI/config parser, even better (preserves comments and ordering).
    #  https://github.com/DiffSK/configobj
    #  https://configobj.readthedocs.io/en/latest/
    'configobj >= 5.0.6',
    # Vocabulary word pluralizer.
    #  https://github.com/ixmatus/inflector
    'Inflector >= 3.0.1, < 4',
    # Amazing prompt library.
    # - Imports as prompt_toolkit.
    # https://github.com/prompt-toolkit/python-prompt-toolkit
    'prompt-toolkit >= 3.0.5, < 4',
    # For the Carousel Fact description lexer.
    #  http://pygments.org/
    'pygments >= 2.6.1, < 3',
    # Just Another EDITOR package.
    #  https://github.com/fmoo/python-editor
    # - Imports as `editor`.
    'python-editor >= 1.0.4, < 2',
    # https://github.com/grantjenks/python-sortedcontainers/
    'sortedcontainers >= 2.1.0, < 3',

    # *** Hamster packages.

    # The heart of Hamster. (Ye olde `hamster-lib`).
    #  https://github.com/hotoffthehamster/nark
    'nark >= 3.0.8, < 4',
    # The controller, config, and common output and error tossing code.
    #  https://github.com/hotoffthehamster/dob-bright
    'dob-bright >= 1.0.9, < 2',
    # The act@gory and tag prompt interface.
    #  https://github.com/hotoffthehamster/dob-prompt
    'dob-prompt >= 1.0.5, < 2',
]

# *** Minimal setup() function -- Prefer using config where possible.

# (lb): Most settings are in setup.cfg, except identifying packages.
# (We could find-packages from within setup.cfg, but it's convoluted.)

setup(
    # Run-time dependencies installed on `pip install`. To learn more
    # about "install_requires" vs pip's requirements files, see:
    #   https://packaging.python.org/en/latest/requirements.html
    install_requires=requirements,

    # Specify which package(s) to install.
    # - Without any rules, find_packages returns, e.g.,
    #     ['dob_viewer', 'tests', 'tests.dob_viewer']
    # - With the 'exclude*' rule, this call is essentially:
    #     packages=['dob_viewer']
    packages=find_packages(exclude=['tests*']),

    # Tell setuptools to determine the version
    # from the latest SCM (git) version tag.
    #
    # Note that if the latest commit is not tagged with a version,
    # or if your working tree or index is dirty, then the version
    # from git will be appended with the commit hash that has the
    # version tag, as well as some sort of 'distance' identifier.
    # E.g., if a project has a '3.0.0a21' version tag but it's not
    # on HEAD, or if the tree or index is dirty, the version might
    # be:
    #   $ python setup.py --version
    #   3.0.0a22.dev3+g6f93d8c.d20190221
    # But if you clean up your working directory and move the tag
    # to the latest commit, you'll get the plain version, e.g.,
    #   $ python setup.py --version
    #   3.0.0a31
    # Ref:
    #   https://github.com/pypa/setuptools_scm
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
)

