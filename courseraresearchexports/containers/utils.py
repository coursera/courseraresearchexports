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

from io import BytesIO
import tarfile
import time


def create_tar_archive(str, name='init-user-db.sh'):
    """Creates tar archive to load single file as suggested by
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
    ports = [container_info.port for container_info in containers_info]

    return max(ports) + 1 if ports else 5433


def is_container_running(container_name_or_id, docker_client):
    """
    Check whether container is still running.
    :param container_name_or_id:
    :param docker_client:
    :return isRunning: Boolean
    """
    container_details = docker_client.inspect_container(container_name_or_id)

    return container_details['State']['Running']
