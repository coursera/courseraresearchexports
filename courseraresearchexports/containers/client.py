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
from courseraresearchexports.constants.api_constants import \
    EXPORT_TYPE_TABLES
from courseraresearchexports.constants.container_constants import \
    COURSERA_DOCKER_LABEL, COURSERA_LOCAL_FOLDER, POSTGRES_DOCKER_IMAGE, \
    POSTGRES_INIT_MSG, POSTGRES_READY_MSG
from courseraresearchexports.containers import utils as container_utils
from courseraresearchexports.exports import utils as export_utils
from courseraresearchexports.models.ContainerInfo import ContainerInfo


def list_all(docker_client):
    """
    Return all containers that have Coursera label
    :param docker_client:
    :return containers_info: [ContainerInfo]
    """
    return [ContainerInfo.from_container(container['Id'], docker_client)
            for container in docker_client.containers(
            all=True, filters={'label': COURSERA_DOCKER_LABEL})]


def start(container_name, docker_client):
    """
    Start a docker container containing a research export database. Waits until
    """
    try:
        logging.debug('Starting container {}...'.format(container_name))
        docker_client.start(container_name)

        # poll logs to see if database is ready to accept connections
        while POSTGRES_READY_MSG not in docker_client.logs(
                container_name, tail=4):

            logging.debug('Polling container for database connection...')
            if not container_utils.is_container_running(
                    container_name, docker_client):
                raise RuntimeError('Container failed to start.')

            time.sleep(10)

        logging.info('Started container {}.'.format(container_name))

    except:
        logging.error(
            """Container failed to start, check log for errors:\n{}"""
            .format(docker_client.logs(container_name, tail=20)))
        raise


def stop(container_name, docker_client):
    """
    Stops a docker container
    """
    docker_client.stop(container_name)


def remove(container_name, docker_client):
    """
    Remove a stopped container
    """
    docker_client.remove_container(container_name)


def initialize(container_name, docker_client):
    """
    Initialize a docker container. Polls database for completion of
    entrypoint tasks.
    """
    try:
        logging.info('Initializing container {}...'.format(
            container_name))

        docker_client.start(container_name)
        while POSTGRES_INIT_MSG not in docker_client.logs(
                container_name, tail=20):

            logging.debug('Polling data for entrypoint initialization...')
            if not container_utils.is_container_running(container_name,
                                                        docker_client):
                raise RuntimeError('Container initialization failed.')

            time.sleep(10)

        logging.info('Initialized container {}.'.format(container_name))

    except:
        logging.error(
            """Container initialization failed, check log for errors:\n{}"""
            .format(docker_client.logs(container_name, tail=20)))
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
    logging.debug('Creating containers from {folder}'.format(
        folder=export_data_folder))
    create_container_args = {
        'volumes': ['/mnt/exportData'],
        'host_config': docker_client.create_host_config(
            binds=['{}:/mnt/exportData:ro'.format(export_data_folder)],
            port_bindings={
                5432: container_utils.get_next_available_port(list_all(
                    docker_client))
            })
    }
    container = create_postgres_container(
        docker_client, container_name, database_name, create_container_args)

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
        data=container_utils.create_tar_archive(
            database_setup_script, name='init-user-db.sh'))

    logging.info('Created container with id: {}'.format(container_id))

    initialize(container_id, docker_client)

    return container_id


def create_postgres_container(docker_client, container_name, database_name,
                              create_container_args):
    if not docker_client.images(name=POSTGRES_DOCKER_IMAGE):
        logging.info('Downloading image: {}'.format(POSTGRES_DOCKER_IMAGE))
        docker_client.import_image(image=POSTGRES_DOCKER_IMAGE)

    for existing_container in docker_client.containers(
            all=True, filters={'name': container_name}):
        logging.info('Removing existing container with name: {}'.format(
            container_name))
        docker_client.stop(existing_container)
        docker_client.remove_container(existing_container)
    create_container_args['image'] = POSTGRES_DOCKER_IMAGE
    create_container_args['name'] = container_name
    create_container_args['labels'] = {
        COURSERA_DOCKER_LABEL: None,
        'database_name': database_name
    }
    return docker_client.create_container(**create_container_args)


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

    if export_request.export_type != EXPORT_TYPE_TABLES:
        raise ValueError('Invalid Export Type. (Only tables exports supported.'
                         'Given [{}])'.format(export_request.export_type))

    logging.info('Downloading export {}'.format(export_request_id))
    downloaded_files = export_utils.download(
        export_request, dest=COURSERA_LOCAL_FOLDER)
    dest = os.path.join(COURSERA_LOCAL_FOLDER, export_request_id)
    for f in downloaded_files:
        container_utils.extract_zip_archive(
            archive=f,
            dest=dest,
            delete_archive=True)

    container_id = create_from_folder(
        export_data_folder=dest,
        docker_client=docker_client,
        database_name=(database_name if database_name
                       else export_request.scope_name),
        container_name=(container_name if container_name
                        else export_request.scope_name)
    )

    shutil.rmtree(dest)

    return container_id
