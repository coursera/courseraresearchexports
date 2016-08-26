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

from courseraresearchexports.containers import utils
from courseraresearchexports import exports
import logging
import shutil
import os
import time


COURSERA_DOCKER_LABEL = 'courseraResearchExport'
COURSERA_LOCAL_FOLDER = os.path.expanduser('~/.coursera/exports/')
POSTGRES_DOCKER_IMAGE = 'postgres:9.5'
POSTGRES_INIT_MSG = 'PostgreSQL init process complete; ready for start up.'
POSTGRES_READY_MSG = 'database system is ready to accept connections'


def get_next_available_port(docker_client):
    """
    Find next available port to map postgres port to host
    :param docker_client:
    :return:
    """
    containers = list_all(docker_client)
    ports = [utils.get_container_host_port(container, docker_client)
             for container in containers]

    return max(ports) + 1 if ports else 5433


def list_all(docker_client):
    """
    Return all containers that have Coursera label
    :param docker_client:
    """
    return docker_client.containers(
        all=True, filters={'label': COURSERA_DOCKER_LABEL})


def start(container, docker_client):
    """
    Start a docker container containing a research export database. Waits until
    """
    logging.info('Starting containers...')
    docker_client.start(container)
    # poll logs to see if database is ready to accept connections
    while POSTGRES_READY_MSG not in docker_client.logs(container, tail=4):
        time.sleep(1)
    logging.info('Container ready.')


def stop(container, docker_client):
    """
    Stops a docker container
    """
    docker_client.stop(container)


def remove(container, docker_client):
    """
    Remove a stopped container
    """
    docker_client.remove_container(container)


def create_from_folder(
        export_data_folder, docker_client, container_name='coursera-exports',
        database_name='coursera-exports'):
    """
    Using a folder containing a Coursera research export, create a docker
     container with the export data loaded into a data base and start the
     container
    :param export_data_folder: folder where export data/scripts is stored
    :param docker_client:
    :param container_name:
    :param database_name:
    :return: container
    """
    try:
        if not docker_client.images(name=POSTGRES_DOCKER_IMAGE):
            logging.warn('Downloading image: {}'.format(POSTGRES_DOCKER_IMAGE))
            docker_client.import_image(image=POSTGRES_DOCKER_IMAGE)

        for existingContainer in docker_client.containers(
                all=True, filters={'name': container_name}):
            logging.info('Removing existing containers: {}'.format(
                container_name))
            docker_client.remove_container(existingContainer, force=True)

        container = docker_client.create_container(
            image=POSTGRES_DOCKER_IMAGE,
            name=container_name,
            labels=[COURSERA_DOCKER_LABEL],
            volumes=['/mnt/exportData'],
            host_config=docker_client.create_host_config(
                binds=['{}:/mnt/exportData:ro'.format(export_data_folder)],
                port_bindings={
                    5432: get_next_available_port(docker_client)
                })
        )

        # copy containers initialization script to entrypoint
        database_setup_script = '''
            createdb -U {0} {1}
            cd /mnt/exportData
            psql -e -U {0} -d {1} -f setup.txt
            psql -e -U {0} -d {1} -f load.txt
        '''.format('postgres', database_name)

        docker_client.put_archive(
            container,  # using a named argument here causes NullResource error
            path='/docker-entrypoint-initdb.d/',
            data=utils.create_tar_archive(
                database_setup_script, name='init-user-db.sh'))

        logging.info('Created containers with id: {}'.format(container['Id']))
        start(container, docker_client)

        # hack to see check if container initialization is done
        logging.info('Initializing container...')
        while POSTGRES_INIT_MSG not in docker_client.logs(container, tail=20):
            time.sleep(1)
        logging.info('Initialization done.')

        return container

    except:
        logging.error('Error setting up container')
        raise


def create_from_export_job_id(export_job_id, docker_client):
    """Creates a containers containers for a given export_job_id"""
    export_job = exports.api.get(export_job_id)

    logging.info('Downloading export {}'.format(export_job_id))
    export_archive = exports.utils.download_export(
        export_job=export_job, dest=COURSERA_LOCAL_FOLDER)
    export_data_folder = exports.utils.extract_export_archive(
            export_archive,
            dest=os.path.join(COURSERA_LOCAL_FOLDER, export_job_id),
            delete_archive=True)

    container = create_from_folder(
        export_data_folder=export_data_folder,
        container_name=export_job_id,
        docker_client=docker_client)

    shutil.rmtree(export_data_folder)

    return container
