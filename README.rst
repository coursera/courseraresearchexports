courseraresearchexports
=======================

.. image:: https://travis-ci.org/coursera/courseraresearchexports.svg
    :target: https://travis-ci.org/coursera/courseraresearchexports

This project is a library consisting of a command line interface and a client
for interacting with Coursera's research exports. Up to date documentation
of the data provided by Coursera for research purposes is available on gitbooks
, `Coursera Data Exports Guide <https://coursera.gitbooks.io/data-exports/content/introduction/programmatic_access.html>`_.

Installation
------------

To install this package, execute::

    pip install courseraresearchexports

`pip <https://pip.pypa.io/en/latest/index.html>`_ is a python package manager.

If you do not have ``pip`` installed on your machine, please follow the
`installation instructions <https://pip.pypa.io/en/latest/installing.html#install-or-upgrade-pip>`_ for your platform.

If you experience issues installing with `pip`, we recommend that you use the
python 2.7 distribution of `Anaconda https://www.continuum.io/downloads`_ and try the above
command again or to use a `virtualenv <https://pypi.python.org/pypi/virtualenv>`_
for installation::

    virtualenv venv
    source venv/bin/activate
    pip install courseraresearchexports

Note: the ``containers`` subcommand requires ``docker`` to already be installed
on your machine. Please see the `docker installation instructions <http://docs.docker.com/index.html>`_ for platform
specific information.

autocomplete
^^^^^^^^^^^^

To enable tab autocomplete, please install `argcomplete <https://github.com/kislyuk/argcomplete>`_ using
``pip install autocomplete`` and execute ``activate-global-python-argcomplete``. Open a new shell and
press tab for autocomplete functionality.

See the argcomplete documentation for more details.

Setup
-----

Authorize your application using `courseraoauth2client <https://github.com/coursera/courseraoauth2client>`_::

    courseraoauth2client config authorize --app manage_research_exports

To use the ``containers`` functionality, a docker instance must be running.
Please see the docker `getting started guide <https://docs.docker.com/engine/getstarted/>`_
for installation instructions for your platform.

Upgrade
-------

If you have a previously installed version of `courseracourseexports`, execute::

    pip install courseraresearchexports --upgrade

This will upgrade your installation to the newest version.

Command Line Interface
----------------------

The project includes a command line tool. Run::

    courseraresearchexports -h

for a complete list of features, flags, and documentation.  Similarly,
documentation for the subcommands listed below is also available (e.g. for
``jobs``) by running::

    courseraresearchexports jobs -h

jobs
^^^^
Submit a research export request or retrieve the status of pending and
completed export jobs.

request
~~~~~~~
Creates an data export job request and return the export request id. To create a
data export requests for all available tables for a course::

    courseraresearchexports jobs request tables --course_slug $COURSE_SLUG \
        --purpose "testing data export"

Replace ``$COURSE_SLUG`` with your course slug (The course slug is the part after
``/learn`` in the url. For ``https://www.coursera.org/learn/machine-learning``,
the slug is `machine-learning`).

If a more limited set of data is required, you can specify which schemas are
included with the export. (e.g. for the demographics tables)::

    courseraresearchexports jobs request tables --course_slug $COURSE_SLUG \
        --schemas demographics --purpose "testing data export"

For more information on the available tables/schemas, please refer to the
`Coursera Data Exports Guide <https://coursera.gitbooks.io/data-exports/content/introduction/programmatic_access.html>`_.

If you are a data coordinator, you can request that user ids are linked between
domains of the data export::

    courseraresearchexports jobs request tables --course_slug $COURSE_SLUG \
        --purpose "testing data export" --user_id_hashing linked

Data coordinators can also request clickstream exports::

    courseraresearchexports jobs request clickstream --course_slug $COURSE_SLUG \
        --interval 2016-09-01 2016-09-02 --purpose "testing data export"

get_all
~~~~~~~
Lists the details and status of all data export requests that you have made::

    courseraresearchexports jobs get_all

get
~~~
Retrieve the details and status of an export request::

    courseraresearchexports jobs get $EXPORT_REQUEST_ID

download
~~~~~~~~
Download a completed table or clickstream to your local destination::

    courseraresearchexports jobs download $EXPORT_REQUEST_ID

clickstream_download_links
~~~~~~~~~~~~~~~~~~~~~~~~~~
Due to the size of clickstream exports, we persist download links for completed
clickstream export requests on Amazon S3. The clickstream data for each day is
saved into a separate file and download links to these files can be retrieved
by running::

    courseraresearchexports jobs clickstream_download_links --course_slug $COURSE_SLUG

containers
^^^^^^^^^^

create
~~~~~~
Creates a docker container using the postgres image and loads export data
into a postgres database on the container.  To create a docker container
from an export, first ``request`` an export using the ``jobs`` command.  Then,
using the ``$EXPORT_REQUEST_ID``, create a docker container with::

    courseraresearchexports containers create --export_request_id $EXPORT_REQUEST_ID

This will download the data export and load all the data into the database
running on the container. This may take some time depending on the size of
your export. To create a docker container with an already downloaded export
(please decompress the archive first)::

    courseraresearchexports containers create --export_data_folder /path/to/data_export/

After creation use the ``list`` command to check the status of the
container and view the container name, database name, address and port to
connect to the database. Use the `db connect $CONTAINER_NAME` command to open
a psql shell.

list
~~~~
Lists the details of all the containers created by ``courseraresearchexports``::

    courseraresearchexports containers list

start
~~~~~
Start a container::

    courseraresearchexports containers start $CONTAINER_NAME

stop
~~~~
Stop a container::

    courseraresearchexports containers stop $CONTAINER_NAME

remove
~~~~~~
Remove a container::

    courseraresearchexports containers remove $CONTAINER_NAME

db
^^

connect
~~~~~~~
Open a shell to a postgres database::

    courseraresearechexports db connect $CONTAINER_NAME

create_view
~~~~~~~~~~~
Create a view in the postgres database. We are planning to include commonly
used denormalized views as part of this project. To create one of these views
(i.e. for the demographic_survey view)::

    courseraresearchexports db create_view $CONTAINER_NAME --view_name demographic_survey

If you have your own sql script that you'd like to create as a view::

    courseraresearchexports db create_view $CONTAINER_NAME --sql_file /path/to/sql/file/

Note: as `user_id` columns vary with partner and user id hashing, please refer
to the exports guide for SQL formatting guidelines.

unload_to_csv
~~~~~~~~~~~~~
Export a table or view to a csv file.  For example, if the `demographic_survey`
was created in the above section, use this commmand to create a csv::

    courseraresearchexports db unload_to_csv $CONTAINER_NAME --relation demographic_survey --dest /path/to/dest/

list_tables
~~~~~~~~~~~
List all the tables present inside a dockerized database::

    courseraresearchexports db list_tables $CONTAINER_NAME

list_views
~~~~~~~~~~
List all the views present inside a dockerized database::

    courseraresearchexports db list_views $CONTAINER_NAME


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
