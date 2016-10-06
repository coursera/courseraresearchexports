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

from courseraresearchexports.containers import client
from courseraresearchexports.containers import utils


def create_container(args):
    """
    Create a container containing a postgres database using an export job id.
    Export job will be downloaded and loaded into dockerized database.
    Automatically starts container.
    """
    d = utils.docker_client(args.docker_url, args.timeout)

    kwargs = {}
    if args.container_name:
        kwargs['container_name'] = args.container_name
    if args.database_name:
        kwargs['database_name'] = args.database_name

    if args.export_request_id:
        container_id = client.create_from_export_request_id(
            args.export_request_id, docker_client=d, **kwargs)
    elif args.export_data_folder:
        container_id = client.create_from_folder(
            args.export_data_folder, docker_client=d, **kwargs)

    logging.info('Container {:.12} ready.'.format(container_id))


def list_containers(args):
    """
    List docker containers created with Coursera data exports.
    """
    d = utils.docker_client(args.docker_url, args.timeout)
    containers_info = client.list_all(docker_client=d)

    if containers_info:
        containers_info_table = [['Name', 'Container Id', 'Database',
                                  'Created', 'Status', 'Host IP', 'Port']]

        for container_info in containers_info:
            containers_info_table.append([
                container_info.name,
                container_info.short_id,
                container_info.database_name,
                container_info.creation_time.strftime('%c'),
                container_info.status,
                container_info.host_ip,
                container_info.host_port
            ])

        print(tabulate(containers_info_table, headers='firstrow'))


def start_container(args):
    """
    Start a docker container.
    """
    d = utils.docker_client(args.docker_url, args.timeout)
    client.start(args.container_name, docker_client=d)


def stop_container(args):
    """
    Stop a docker container.
    """
    d = utils.docker_client(args.docker_url, args.timeout)
    client.stop(args.container_name, docker_client=d)


def remove_container(args):
    """
    Remove a docker container, stop the container
    before removing.
    """
    d = utils.docker_client(args.docker_url, args.timeout)
    client.remove(args.container_name, docker_client=d)


def parser(subparsers):
    parser_containers = subparsers.add_parser(
        'containers',
        help='Create docker container from export jobs',
        description='Command line tools for creating a docker container'
        'containing the results of a research export. Please first '
        'authenticate with the OAuth2 client before making requests ('
        'courseraoauth2client config authorize --app manage-research-exports)',
        epilog='Please file bugs on github at: '
        'https://github.com/coursera/courseraresearchexports/issues. If you '
        'would like to contribute to this tool\'s development, check us out '
        'at: https://github.com/coursera/courseraresarchexports',
        parents=[utils.docker_client_arg_parser()])

    containers_subparsers = parser_containers.add_subparsers()

    parser_create = containers_subparsers.add_parser(
        'create',
        help=create_container.__doc__,
        description=create_container.__doc__)
    parser_create.set_defaults(func=create_container)

    source_subparser = parser_create.add_mutually_exclusive_group(
        required=True)

    source_subparser.add_argument(
        '--export_request_id',
        help='Export job to download and create containers')
    source_subparser.add_argument(
        '--export_data_folder',
        help='Location of already downloaded export data')

    parser_create.add_argument(
        '--container_name',
        help='Name for docker container.')
    parser_create.add_argument(
        '--database_name',
        help='Name for database inside container.')

    parser_list = containers_subparsers.add_parser(
        'list',
        help=list_containers.__doc__)
    parser_list.set_defaults(func=list_containers)

    parser_stop = containers_subparsers.add_parser(
        'stop',
        help=stop_container.__doc__)
    parser_stop.add_argument(
        'container_name',
        help='Name of the container to stop.')
    parser_stop.set_defaults(func=stop_container)

    parser_start = containers_subparsers.add_parser(
        'start',
        help=start_container.__doc__)
    parser_start.add_argument(
        'container_name',
        help='Name of the container to start.')
    parser_start.set_defaults(func=start_container)

    parser_remove = containers_subparsers.add_parser(
        'remove',
        help=remove_container.__doc__)
    parser_remove.add_argument(
        'container_name',
        help='Name of the container to remove.')
    parser_remove.set_defaults(func=remove_container)

    return parser_containers
