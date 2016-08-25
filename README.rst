courseraresearchexports
====================

.. image:: https://travis-ci.org/coursera/courseraresearchexports.svg
    :target: https://travis-ci.org/coursera/courseraresearchexports

This project is a library consisting of a command line interface and a client
for interacting with Coursera's research exports.

Installation
------------

To install this sdk, simply execute::

    sudo pip install courseraresearchexports

`pip <https://pip.pypa.io/en/latest/index.html>`_ is a python package manager.
If you do not have ``pip`` installed on your machine, please follow the
installation instructions for your platform found at:
https://pip.pypa.io/en/latest/installing.html#install-or-upgrade-pip

Setup
-----

Authorize your application by running ``courseraresearchexports config authorize``


Command Line Interface
----------------------

The project includes a command line tool. Simply run::

    courseraresearchexports -h

for a complete list of features, flags, and documentation.


config
^^^^^^

Configures the Coursera OAuth2 client library.

Examples:
 - ``courseraresearchexports config authorize``

   Configures the tool to go through the `authorization secret <https://tools.ietf.org/html/rfc6749#section-4.1>`_ flow for application ``manage-research-exports``.
 - ``courseraresearchexports config check-auth``

   Checks whether the current instance can authorize against Coursera's API server for application ``manage-research-exports``

Usage
-----------


Bugs / Issues / Feature Requests
--------------------------------

Please us the github issue tracker to document any bugs or other issues you
encounter while using this tool.


Developing / Contributing
-------------------------

We recommend developing ``courseraresearchexports`` within a python
`virtualenv <https://pypi.python.org/pypi/virtualenv>`_.
To get your environment set up properly, do the following::

    virtualenv venv
    source venv/bin/activate
    python setup.py develop
    pip install -r test_requirements.txt

Tests
^^^^^

To run tests, simply run: ``nosetests``, or ``tox``.

Code Style
^^^^^^^^^^

Code should conform to pep8 style requirements. To check, simply run::

    pep8 courseraresearchexports tests
