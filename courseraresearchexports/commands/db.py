# Copyright 2016 Coursera
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import logging

from tabulate import tabulate

import courseraresearchexports.db.db as db
from courseraresearchexports.containers import utils


def connect(args):
    """
    Connect postgres shell to dockerized database.
    """
    d = utils.docker_client(args.docker_url, args.timeout)
    db.connect(args.container_name, docker_client=d)


def list_tables(args):
    """
    List all of the tables present in a dockerized database.
    """
    d = utils.docker_client(args.docker_url, args.timeout)
    tables = db.get_table_names(args.container_name, docker_client=d)
    print(tabulate([[table] for table in tables]))


def list_views(args):
    """
    List all of the views present in a dockerized database.
    """
    d = utils.docker_client(args.docker_url, args.timeout)
    tables = db.get_view_names(args.container_name, docker_client=d)
    print(tabulate([[table] for table in tables]))


def create_view(args):
    """
    Create a view from a sql query.
    """
    d = utils.docker_client(args.docker_url, args.timeout)

    if args.view_name:
        created_view = db.create_registered_view(
            args.container_name, args.view_name, d)
    elif args.sql_file:
        created_view = db.create_view_from_file(
            args.container_name, args.sql_file, d)

    logging.info('Created view {}'.format(created_view))


def unload_relation(args):
    """
    Unload a table or view to a CSV file.
    """
    d = utils.docker_client(args.docker_url, args.timeout)
    rowcount = db.unload_relation(args.container_name, args.dest,
                                  args.relation, d)

    logging.info('Unloaded {} rows'.format(rowcount))


def parser(subparsers):
    """Build an argparse argument parser to parse the command line."""

    # create the parser for the version subcommand.
    parser_db = subparsers.add_parser(
        'db',
        help='Tools for interacting with dockerized database',
        parents=[utils.docker_client_arg_parser()])

    db_subparsers = parser_db.add_subparsers()

    parser_tables = db_subparsers.add_parser(
        'list_tables',
        help=list_tables.__doc__)
    parser_tables.set_defaults(func=list_tables)
    parser_tables.add_argument(
        'container_name',
        help='Name of the container database.')

    parser_views = db_subparsers.add_parser(
        'list_views',
        help=list_views.__doc__)
    parser_views.set_defaults(func=list_views)
    parser_views.add_argument(
        'container_name',
        help='Name of the container database.')

    parser_create_view = db_subparsers.add_parser(
        'create_view',
        help=create_view.__doc__)
    parser_create_view.set_defaults(func=create_view)
    parser_create_view.add_argument(
        'container_name',
        help='Name of the container database.')
    create_source_subparser = parser_create_view.add_mutually_exclusive_group(
        required=True)
    create_source_subparser.add_argument(
        '--view_name',
        help='Name of view')
    create_source_subparser.add_argument(
        '--sql_file',
        help='SQL file with query.')

    parser_unload = db_subparsers.add_parser(
        'unload_to_csv',
        help=unload_relation.__doc__)
    parser_unload.set_defaults(func=unload_relation)
    parser_unload.add_argument(
        'container_name',
        help='Name of the container database.')
    parser_unload.add_argument(
        '--dest',
        help='Destination folder.')
    parser_unload.add_argument(
        '--relation',
        help='Table or view to export.')

    parser_connect = db_subparsers.add_parser(
        'connect',
        help=connect.__doc__)
    parser_connect.set_defaults(func=connect)
    parser_connect.add_argument(
        'container_name',
        help='Name of the container database.')

    return parser_db
