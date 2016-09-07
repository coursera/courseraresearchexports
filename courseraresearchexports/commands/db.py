#!/usr/bin/env python

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

import logging
from tabulate import tabulate

import courseraresearchexports.db.db as db
import courseraresearchexports.utils.container_utils as container_utils


def list_tables(args):
    d = container_utils.docker_client(args.docker_url, args.timeout)
    tables = db.get_table_names(args.container_name_or_id, docker_client=d)
    logging.info('\n' + tabulate([[table] for table in tables]))


def list_views(args):
    d = container_utils.docker_client(args.docker_url, args.timeout)
    tables = db.get_view_names(args.container_name_or_id, docker_client=d)
    logging.info('\n' + tabulate([[table] for table in tables]))


def create_view(args):
    d = container_utils.docker_client(args.docker_url, args.timeout)
    db.create_view(args.container_name_or_id, args.sql_file, args.partner_short_name, d)


def unload_relation(args):
    d = container_utils.docker_client(args.docker_url, args.timeout)
    db.unload_relation(args.container_name_or_id, args.dest, args.relation, d)


def parser(subparsers):
    """Build an argparse argument parser to parse the command line."""

    # create the parser for the version subcommand.
    parser_db= subparsers.add_parser(
        'db',
        help='Stuff with DB',
        parents=[container_utils.docker_client_arg_parser()])

    parser_db.add_argument(
        'container_name_or_id',
        help='Name or id of container container database.')

    db_subparsers = parser_db.add_subparsers()

    parser_tables = db_subparsers.add_parser(
        'list_tables',
        help=list_tables.__doc__)
    parser_tables.set_defaults(func=list_tables)

    parser_views = db_subparsers.add_parser(
        'list_views',
        help=list_views.__doc__)
    parser_views.set_defaults(func=list_views)

    parser_create_view = db_subparsers.add_parser(
        'create_view',
        help=create_view.__doc__)
    parser_create_view.set_defaults(func=create_view)

    parser_create_view.add_argument(
        '--sql_file',
        help='Name of sql file containing select statement to create view.'
    )

    parser_create_view.add_argument(
        '--partner_short_name',
        help='Your partner short name.'
    )

    parser_unload = db_subparsers.add_parser(
        'unload_to_csv',
        help=unload_relation.__doc__)
    parser_unload.set_defaults(func=unload_relation)

    parser_unload.add_argument(
        '--dest',
        help='CSV file to create.'
    )

    parser_unload.add_argument(
        '--relation',
        help='Table or view to export.'
    )

    return parser_db
