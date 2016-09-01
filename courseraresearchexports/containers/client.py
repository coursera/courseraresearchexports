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

"""
Coursera's tools for managing docker containers configured with a
postgres database.
"""

import logging
import os
import shutil
import time

from courseraresearchexports import exports
from courseraresearchexports.containers import utils
from courseraresearchexports.models.ContainerInfo import ContainerInfo


COURSERA_DOCKER_LABEL = 'courseraResearchExport'
COURSERA_LOCAL_FOLDER = os.path.expanduser('~/.coursera/exports/')
POSTGRES_DOCKER_IMAGE = 'postgres:9.5'
POSTGRES_INIT_MSG = 'PostgreSQL init process complete; ready for start up.'
POSTGRES_READY_MSG = 'database system is ready to accept connections'


def list_all(docker_client):
    """
    Return all containers that have Coursera label
    :param docker_client:
    :return containers_info: [ContainerInfo]
    """
    return [ContainerInfo.from_container_dict(
            docker_client.inspect_container(container))
            for container in docker_client.containers(
            all=True, filters={'label': COURSERA_DOCKER_LABEL})]


def start(container_name_or_id, docker_client):
    """
    Start a docker container containing a research export database. Waits until
    """
    try:
        logging.debug('Starting container {}...'.format(container_name_or_id))
        docker_client.start(container_name_or_id)

        # poll logs to see if database is ready to accept connections
        while POSTGRES_READY_MSG not in docker_client.logs(
                container_name_or_id, tail=4):

            logging.debug('Polling container for database connection...')
            if not utils.is_container_running(
                    container_name_or_id, docker_client):
                raise RuntimeError('Container failed to start.')

            time.sleep(10)

        logging.info('Started container {}.'.format(container_name_or_id))

    except:
        logging.error(
            """Container failed to start, check log for errors:\n{}"""
            .format(docker_client.logs(container_name_or_id, tail=20)))
        raise


def stop(container_name_or_id, docker_client):
    """
    Stops a docker container
    """
    docker_client.stop(container_name_or_id)


def remove(container_name_or_id, docker_client):
    """
    Remove a stopped container
    """
    docker_client.remove_container(container_name_or_id)


def initialize(container_name_or_id, docker_client):
    """
    Initialize a docker container. Polls database for completion of
    entrypoint tasks.
    """
    try:
        logging.info('Initializing container {}...'.format(
            container_name_or_id))

        docker_client.start(container_name_or_id)
        while POSTGRES_INIT_MSG not in docker_client.logs(
                container_name_or_id, tail=20):

            logging.debug('Polling data for entrypoint initialization...')
            if not utils.is_container_running(container_name_or_id,
                                              docker_client):
                raise RuntimeError('Container initialization failed.')

            time.sleep(10)

        logging.info('Initialized container {}.'.format(container_name_or_id))

    except:
        logging.error(
            """Container initialization failed, check log for errors:\n{}"""
            .format(docker_client.logs(container_name_or_id, tail=20)))
        logging.error(
            """If error persists, consider restarting your docker engine.""")
        raise


def create_from_folder(export_data_folder, docker_client,
                       container_name='coursera-exports',
                       database_name='coursera-exports'):
    """
    Using a folder containing a Coursera research export, create a docker
     container with the export data loaded into a data base and start the
     container
    :param export_data_folder: folder where export data/scripts is stored
    :param docker_client:
    :param container_name:
    :param database_name:
    :return container_id:
    """
    if not docker_client.images(name=POSTGRES_DOCKER_IMAGE):
        logging.info('Downloading image: {}'.format(POSTGRES_DOCKER_IMAGE))
        docker_client.import_image(image=POSTGRES_DOCKER_IMAGE)

    for existing_container in docker_client.containers(
            all=True, filters={'name': container_name}):
        logging.info('Removing existing container with name: {}'.format(
            container_name))
        docker_client.stop(existing_container)
        docker_client.remove_container(existing_container)

    logging.debug('Creating containers from {folder}'.format(
        folder=export_data_folder))
    container = docker_client.create_container(
        image=POSTGRES_DOCKER_IMAGE,
        name=container_name,
        labels={COURSERA_DOCKER_LABEL: None, 'database_name': database_name},
        volumes=['/mnt/exportData'],
        host_config=docker_client.create_host_config(
            binds=['{}:/mnt/exportData:ro'.format(export_data_folder)],
            port_bindings={
                5432: utils.get_next_available_port(list_all(
                    docker_client))
            }))

    container_id = container['Id']

    # copy containers initialization script to entrypoint
    database_setup_script = """
        createdb -U {user} {db}
        cd /mnt/exportData
        psql -e -U {user} -d {db} -f setup.sql
        psql -e -U {user} -d {db} -f load.sql
    """.format(user='postgres', db=database_name)

    docker_client.put_archive(
        container_id,  # using a named argument causes NullResource error
        path='/docker-entrypoint-initdb.d/',
        data=utils.create_tar_archive(
            database_setup_script, name='init-user-db.sh'))

    logging.info('Created container with id: {}'.format(container_id))

    initialize(container_id, docker_client)

    return container_id


def create_from_export_request_id(export_request_id, docker_client,
                                  container_name=None, database_name=None):
    """
    Create a docker container containing the export data from a given
    export request. Container and database name will be inferred as the
    course slug or partner short name from export_request if not provided.
    :param export_request_id:
    :param docker_client:
    :param container_name:
    :param database_name:
    :return container_id:
    """
    export_request = exports.api.get(export_request_id)[0]

    if export_request.export_type != exports.constants.EXPORT_TYPE_TABLES:
        logging.error('Sorry, container creation is only available with '
                      'tables data exports.')
        raise ValueError('Invalid Export Type.')

    logging.info('Downloading export {}'.format(export_request_id))
    export_archive = export_request.download(dest=COURSERA_LOCAL_FOLDER)
    export_data_folder = exports.utils.extract_export_archive(
            export_archive,
            dest=os.path.join(COURSERA_LOCAL_FOLDER, export_request_id),
            delete_archive=True)

    container_id = create_from_folder(
        export_data_folder=export_data_folder,
        docker_client=docker_client,
        database_name=(database_name if database_name
                       else export_request.scope_name),
        container_name=(container_name if container_name
                        else export_request.scope_name)
    )

    shutil.rmtree(export_data_folder)

    return container_id
