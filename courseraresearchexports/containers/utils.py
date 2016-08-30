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


def get_container_host_ip_and_port(container, docker_client):
    """
    Find bound host port to postgres port
    :param container:
    :param docker_client:
    :return ip, port:
    """
    container_info = docker_client.inspect_container(container)
    port_bindings = container_info['NetworkSettings']['Ports']['5432/tcp'][0]
    return port_bindings['HostIp'], int(port_bindings['HostPort'])
