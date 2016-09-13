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

import dateutil.parser


class ContainerInfo:
    """
    Represents the relevant information about a docker container used to store
    a database of Coursera Export data.
    """

    def __init__(self, name=None, id=None, host_port=None, host_ip=None,
                 creation_time=None, database_name=None, status=None):
        self.name = name
        self.id = id
        self.short_id = id[:12] if id else None
        self.host_port = host_port
        self.host_ip = host_ip
        self.creation_time = creation_time
        self.status = status
        self.database_name = database_name

    @classmethod
    def from_container(cls, container_name, docker_client):
        """
        Create ContainerInfo using the response from docker-py Client's
        `inspect-container` method.
        :param container_dict:
        :return container_info: ContainerInfo
        """
        container_dict = docker_client.inspect_container(container_name)
        host_config = container_dict['HostConfig']['PortBindings']
        network_settings = container_dict['NetworkSettings']['Ports']

        assigned_port = int(host_config['5432/tcp'][0]['HostPort'])
        ip_if_running = network_settings and network_settings[
            '5432/tcp'][0]['HostIp']

        return cls(
            name=container_dict['Name'][1:],  # remove prepended '\'
            id=container_dict['Id'],
            creation_time=dateutil.parser.parse(container_dict['Created']),
            database_name=container_dict['Config']['Labels']['database_name'],
            status=container_dict['State']['Status'],
            host_port=assigned_port,
            host_ip=ip_if_running)
