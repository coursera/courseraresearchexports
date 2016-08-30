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
from datetime import datetime


class ContainerInfo:
    """
    Represents the relevant information about a docker container used to store
    a database of Coursera Export data.
    """

    def __init__(self, name=None, id=None, host_port=None, host_ip=None,
                 creation_time=None, status=None):
        self.name = name
        self.id = id
        self.short_id = id[:12] if id else None
        self.host_port = host_port
        self.host_ip = host_ip
        self.creation_time = creation_time
        self.status = status

    @staticmethod
    def from_container_dict(container_dict):
        """
        Create ContainerInfo using the response from docker-py Client's
        `containers` method.
        :param container_dict:
        :return container_info: ContainerInfo
        """
        ip, port = get_container_host_ip_and_port(container_dict)
        return ContainerInfo(
            name=container_dict['Names'][0][1:],  # remove prepended '\'
            id=container_dict['Id'],
            creation_time=datetime.fromtimestamp(container_dict['Created']),
            status=container_dict['Status'],
            host_port=port,
            host_ip=ip)


def get_container_host_ip_and_port(container_dict):
    """
    Find host port bound to postgres port
    :param container_dict: as returned by docker-py.Client.containers()
    :return ip, port:
    """
    ip = container_dict['Ports'][0]['IP']
    port = container_dict['Ports'][0]['PublicPort']
    return ip, port
