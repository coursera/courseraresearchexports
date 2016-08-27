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

from courseraresearchexports.containers import client, utils
from courseraresearchexports.utils import docker_client
from datetime import datetime
from tabulate import tabulate
import logging
import sys


def create_container(args):
    """
    Create a container containing a postgres database using an export job id.
    Export job will be downloaded and loaded into dockerized database.
    Automatically starts container.
    """
    try:
        d = docker_client(args)
        container = client.create_from_export_job_id(
            export_job_id=args.exportJobId, docker_client=d)
        logging.info('Created container %s', container['Id'])

    except Exception as e:
        logging.error('Error creating container with job %s:\n%s',
                      args.exportJobId, e)
        sys.exit(1)


def list_containers(args):
    """
    List docker containers created with Coursera data exports.
    """
    d = docker_client(args)
    containers = client.list_all(docker_client=d)

    if containers:
        containers_info = [['Name', 'Container Id', 'Created', 'Status', 'IP',
                            'Port']]
        for container in containers:
            creation_time = datetime.fromtimestamp(
                container['Created']).strftime('%Y-%m-%d %H:%M')
            ip, port = utils.get_container_host_ip_and_port(
                container, docker_client=d)
            containers_info.append([
                container['Names'][0][1:],
                container['Id'][:12],
                creation_time,
                container['Status'],
                ip,
                port
            ])

        logging.info('\n' + tabulate(containers_info, headers='firstrow'))


def start_container(args):
    """
    Start a docker container.
    """
    d = docker_client(args)
    client.start(args.containerName, docker_client=d)


def stop_container(args):
    """
    Stop a docker container.
    """
    d = docker_client(args)
    client.stop(args.containerName, docker_client=d)


def remove_container(args):
    """
    Remove a docker container, does not force so stop the container
    before removing.
    """
    d = docker_client(args)
    client.remove(args.containerName, docker_client=d)


def parser(subparsers):
    parser_containers = subparsers.add_parser(
        'containers',
        help='Create docker container from export jobs') \

    containers_subparsers = parser_containers.add_subparsers()

    parser_create = containers_subparsers.add_parser(
        'create',
        help=create_container.__doc__)
    parser_create.set_defaults(func=create_container)
    parser_create.add_argument(
        'exportJobId',
        help='Export job to download and create containers')
    # parser_createContainer.add_argument(
    #     '--containerName',
    #     help='Name for docker containers.')
    # parser_createContainer.add_argument(
    #     '--databaseName'
    #     help='Name for containers inside containers')

    parser_list = containers_subparsers.add_parser(
        'list',
        help=list_containers.__doc__)
    parser_list.set_defaults(func=list_containers)

    parser_stop = containers_subparsers.add_parser(
        'stop',
        help=stop_container.__doc__)
    parser_stop.add_argument(
        'containerName',
        help='Name of container to be stopped')
    parser_stop.set_defaults(func=stop_container)

    parser_start = containers_subparsers.add_parser(
        'start',
        help=start_container.__doc__)
    parser_start.add_argument(
        'containerName',
        help='Name of containers to be started')
    parser_start.set_defaults(func=start_container)

    parser_remove = containers_subparsers.add_parser(
        'remove',
        help=remove_container.__doc__)
    parser_remove.add_argument(
        'containerName',
        help='Name of containers to be removed')
    parser_remove.set_defaults(func=remove_container)

    return parser_containers
