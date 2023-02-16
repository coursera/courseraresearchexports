courseraresearchexports
=======================

.. image:: https://travis-ci.org/coursera/courseraresearchexports.svg
    :target: https://travis-ci.org/coursera/courseraresearchexports

This project is a library consisting of a command line interface and a client
for interacting with Coursera's research exports. Up to date documentation
of the data provided by Coursera for research purposes is available in the Partner Resource Center
, `Coursera Data Exports Guide <https://partner.coursera.help/hc/articles/360021121132/>`_.

Installation
------------

To install this package, execute::

    pip install courseraresearchexports

`pip <https://pip.pypa.io/en/latest/index.html>`_ is a python package manager.

If you do not have ``pip`` installed on your machine, please follow the
`installation instructions <https://pip.pypa.io/en/latest/installing.html#install-or-upgrade-pip>`_ for your platform.

If you experience issues installing with `pip`, we recommend that you use the
python 2.7 distribution of `Anaconda <https://docs.conda.io/en/latest/miniconda.html>`_ and try the above
command again or to use a `virtualenv <https://pypi.python.org/pypi/virtualenv>`_
for installation::

    virtualenv venv -p python2.7
    source venv/bin/activate
    pip install courseraresearchexports

Note: the ``containers`` subcommand requires ``docker`` to already be installed
on your machine. Please see the `docker installation instructions <http://docs.docker.com/index.html>`_ for platform
specific information.

Refer to `Issues`_ section for additional debugging around installation.

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

    courseraresearchexports jobs request tables --course_id $COURSE_ID \
        --purpose "testing data export"

In order to know your course_id, you can take advantage
of our COURSE API, putting in the appropriate course_slug. 

For example,
if the course_slug is `developer-iot`, you can query the course_id by making the request in your browser logged in session::

    https://api.coursera.org/api/onDemandCourses.v1?q=slug&slug=developer-iot

The response will be a JSON object containing an id field with the value::

    iRl53_BWEeW4_wr--Yv6Aw

**Note**: The course slug is the part after
``/learn`` in your course url. For ``https://www.coursera.org/learn/machine-learning``,
the slug is `machine-learning`

If you have a publically available course, you can request the export using::

    courseraresearchexports jobs request tables --course_slug $COURSE_SLUG \
        --purpose "testing data export"

Replace ``$COURSE_SLUG`` with your course slug (The course slug is the part after
``/learn`` in the url. For ``https://www.coursera.org/learn/machine-learning``,
the slug is `machine-learning`).

If a more limited set of data is required, you can specify which schemas are
included with the export. (e.g. for the demographics and notebooks tables)::

    courseraresearchexports jobs request tables --course_id $COURSE_ID \
        --schemas demographics notebooks --purpose "testing data export"

You can look at all the possible ways to export using::

    courseraresearchexports jobs request tables -h

**Recommendations**


1. Always request the specific schemas that you need by adding the `schemas` while requesting the exports.  
For more information on the available tables/schemas, please refer to the
`Coursera Data Exports Guide <https://partner.coursera.help/hc/articles/360021121132/>`_.

2. While requesting the exports for all courses in your institution, it is recommended to use the partner level export,
rather than requesting individual course level exports. You can use the command::

    courseraresearchexports jobs request tables --partner_short_name $PARTNER_SHORT_NAME \
        --schemas demographics notebooks --purpose "testing data export"

Your partner_short_name can be found in the University Assets section of your institution setting.
 
Note that the above command is available for only publicly available partners.
If you have your partnerID, you can request the export using::

    courseraresearchexports jobs request tables --partner_id $PARTNER_ID \
        --schemas demographics notebooks --purpose "testing data export"

You can find your partner_id using the API in your browser login session::
    https://www.coursera.org/api/partners.v1?q=shortName&shortName=$PARTNER_SHORT_NAME

If you are a data coordinator, you can request that user ids are linked between
domains of the data export::

    courseraresearchexports jobs request tables --course_id $COURSE_ID \
        --purpose "testing data export" --user_id_hashing linked

Data coordinators can also request clickstream exports::

    courseraresearchexports jobs request clickstream --course_id $COURSE_ID \
        --interval 2016-09-01 2016-09-02 --purpose "testing data export"

By default, clickstream exports will cache results for days already exported. To ignore the cache and request exports for the entire date range, pass in the flag ``--ignore_existing``.

Rate limits
~~~~~~~~~~~
We have rate limits enabled for the number of exports that can be performed. The underlying export API returns the rate limit error message, 
which is printed when the command fails. The error message reflects the reason why you might be rate limited.

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

    courseraresearchexports jobs clickstream_download_links --course_id $COURSE_ID

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

    courseraresearchexports db connect $CONTAINER_NAME

create_view
~~~~~~~~~~~
Create a view in the postgres database. We are planning to include commonly
used denormalized views as part of this project. To create one of these views
(i.e. for the demographic_survey view)::

    courseraresearchexports db create_view $CONTAINER_NAME --view_name demographic_survey

If you have your own sql script that you'd like to create as a view run::

    courseraresearchexports db create_view $CONTAINER_NAME --sql_file /path/to/sql/file/new_view.sql

This will create a view using the name of the file as the name of the view, in this case "new_view".

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
    
Using `courseraresearchexports` on a machine without a browser
--------------------------------------------------------------
Sometimes, a browser is not available, making the oauth flow not possible. Commonly, this occurs when users want to automate the data export process by using an external machine.

To get around this, you may generate the access token initially on a machine with browser access [e.g your laptop]. The access token is serialized in your local file system at `~/.coursera/manage_research_exports_oauth2_cache.pickle`.

Requests after the first can use the refresh token flow, which does not require a browser. By copying the initial pickled access token to a remote machine, that machine can continue to request updated data. 



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


Issues
-------
If you face following error when installling psycopg2 package for Mac::

    ld: library not found for -lssl
    clang: error: linker command failed with exit code 1 (use -v to see invocation)
    error: command 'gcc' failed with exit status 1

Install openssl package if not installed::

    brew install openssl
    export LDFLAGS="-L/usr/local/opt/openssl/lib"
    or 
    export LDFLAGS=-L/usr/local/opt/openssl@3/lib

