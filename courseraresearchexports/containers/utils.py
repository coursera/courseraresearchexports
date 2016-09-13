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

import argparse
from io import BytesIO
import logging
import os
import tarfile
import time
import zipfile

from docker import Client


def extract_zip_archive(archive, dest, delete_archive=True):
    """
    Extracts a zip archive to `dest`
    :param export_archive:
    :param dest:
    :param delete_archive: delete the archive after extracting
    :return dest:
    """
    try:
        logging.debug('Extracting archive to {}'.format(dest))
        with zipfile.ZipFile(archive, 'r') as z:
            z.extractall(dest)
        if delete_archive:
            os.remove(archive)
    except:
        logging.error('Error in extracting zip archive {} to {}'.format(
            archive, dest))
        raise


def create_tar_archive(str, name='init-user-db.sh'):
    """
    Creates tar archive to load single file as suggested by
    https://gist.github.com/zbyte64/6800eae10ce082bb78f0b7a2cca5cbc2
    """
    archive_tarstream = BytesIO()
    archive_file = tarfile.TarFile(fileobj=archive_tarstream, mode='w')

    file_data = str.encode('utf8')
    file_info = tarfile.TarInfo(name)
    file_info.size = len(file_data)
    file_info.mtime = time.time()

    archive_file.addfile(file_info, BytesIO(file_data))
    archive_file.close()
    archive_tarstream.seek(0)

    return archive_tarstream


def get_next_available_port(containers_info):
    """
    Find next available port to map postgres port to host.
    :param containers_info:
    :return port:
    """
    ports = [container_info.host_port for container_info in containers_info]

    return (max(ports) + 1) if ports else 5433


def is_container_running(container_name, docker_client):
    """
    Check whether container is still running.
    :param container_name:
    :param docker_client:
    :return isRunning: Boolean
    """
    container_details = docker_client.inspect_container(container_name)

    return container_details['State']['Running']


def docker_client_arg_parser():
    """Builds an argparse parser for docker client connection flags."""
    # The following subcommands operate on a single containers. We centralize
    # all these options here.
    docker_parser = argparse.ArgumentParser(add_help=False)
    docker_parser.add_argument(
        '--docker-url',
        help='The url of the docker demon.')
    docker_parser.add_argument(
        '--timeout',
        type=int,
        default=60,
        help='Set the default timeout when interacting with the docker demon')
    return docker_parser


def docker_client(docker_url=None, timeout=60):
    """
    Attempts to create a docker client.

     - docker_url: base url for docker
     - timeout: timeout for docker client
     - returns: a docker-py client
    """
    if docker_url:
        return Client(
            base_url=docker_url,
            timeout=timeout,
            version='auto')
    else:
        return Client(
            timeout=timeout,
            version='auto')
