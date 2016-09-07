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


from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey
import csv
import os

from courseraresearchexports.models.ContainerInfo import ContainerInfo
from courseraresearchexports.models.ExportDb import ExportDb


def get_table_names(container_name_or_id, docker_client):
    """
    Returns table names present in containerized database.
    :param container_name_or_id:
    :param docker_client:
    :return table_names:
    """
    container_info = ContainerInfo.from_container_dict(
        docker_client.inspect_container(container_name_or_id))
    export_db = ExportDb.from_container_info(container_info)

    return export_db.tables


def get_view_names(container_name_or_id, docker_client):
    """
    Returns view names present in containerized database.
    :param container_name_or_id:
    :param docker_client:
    :return table_names:
    """
    container_info = ContainerInfo.from_container_dict(
        docker_client.inspect_container(container_name_or_id))
    export_db = ExportDb.from_container_info(container_info)

    return export_db.views


def unload_relation(container_name_or_id, dest_file, relation, docker_client):
    container_info = ContainerInfo.from_container_dict(
        docker_client.inspect_container(container_name_or_id))
    export_db = ExportDb.from_container_info(container_info)

    export_db.unload_relation(dest_file, relation)


def create_view(container_name_or_id, sql_file, partner_short_name, docker_client):
    container_info = ContainerInfo.from_container_dict(
        docker_client.inspect_container(container_name_or_id))
    export_db = ExportDb.from_container_info(container_info)

    with open(sql_file, 'r') as sf:
        sql_text = sf.read()

    sql_text_with_partner_short_name = sql_text.replace(
        '[partner_short_name]', partner_short_name)

    view_name = os.path.splitext(os.path.basename(sql_file))[0]

    export_db.create_view(view_name, sql_text_with_partner_short_name)
