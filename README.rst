courseraresearchexports
=======================

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

Authorize your application using `courseraoauth2client <https://github.com/coursera/courseraoauth2client>`_::

    courseraoauth2client config authorize --app manage-research-exports

Command Line Interface
----------------------

The project includes a command line tool. Simply run::

    courseraresearchexports -h

for a complete list of features, flags, and documentation.

jobs
^^^^

create
~~~~~~

Create an data export job request and return the export job id.  There are two
general workflows for creating data export requests.  To create a data export
requests for all available schemas for a course::

    courseraresearchexports jobs create schemas --courseId $COURSE_ID --statementOfPurpose "testing data export"

If a more limited set of data is required, you can specify which schemas are
included with the export.  (e.g. for the demographics tables)::

    courseraresearchexports jobs create schemas --courseId $COURSE_ID --schemas demographics --statementOfPurpose "testing data export"

If you are a data coordinator, you can request that user ids are linked between
domains of the data export::

    courseraresearchexports jobs create schemas --courseId $COURSE_ID --statementOfPurpose "testing data export" --anonymityLevel HASHED_IDS_NO_PII

Data coordinators can also request clickstream (eventing) exports::

    courseraresearchexports jobs create eventing --courseId $COURSE_ID --interval 2016-09-01 2016-09-02 --anonymityLevel HASHED_IDS_NO_PII --statementOfPurpose "testing data export"

getAll
~~~~~~

Lists the details and status of all data export requests that you have made::

    courseraresearchexports jobs getAll

get
~~~

Retrieve the details and status of an export job::

    courseraresearchexports jobs get $EXPORT_JOB_ID

containers
^^^^^^^^^^

Usage
-----


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
