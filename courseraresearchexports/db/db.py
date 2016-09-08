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

import os
import logging
import pkg_resources

from courseraresearchexports.models.ExportDb import ExportDb


def get_table_names(container_name_or_id, docker_client):
    """
    Returns table names present in containerized database.
    :param container_name_or_id:
    :param docker_client:
    :return table_names:
    """
    export_db = ExportDb.from_container(container_name_or_id, docker_client)

    return export_db.tables


def get_view_names(container_name_or_id, docker_client):
    """
    Returns view names present in containerized database.
    :param container_name_or_id:
    :param docker_client:
    :return table_names:
    """
    export_db = ExportDb.from_container(container_name_or_id, docker_client)

    return export_db.views


def unload_relation(container_name_or_id, dest, relation, docker_client):
    """
    Unloads a table or view to a csv file.
    :param container_name_or_id:
    :param dest_file:
    :param relation:
    :param docker_client:
    :return:
    """
    if not os.path.exists(dest):
        logging.debug('Creating destination folder: {}'.format(dest))
        os.makedirs(dest)

    export_db = ExportDb.from_container(container_name_or_id, docker_client)
    output_filename = os.path.join(dest, '{}.csv'.format(relation))
    export_db.unload_relation(relation, output_filename)


def create_view(container_name_or_id, view_name, partner_short_name,
                docker_client):
    """

    :param container_name_or_id:
    :param view_name:
    :param partner_short_name:
    :param docker_client:
    :return:
    """
    export_db = ExportDb.from_container(container_name_or_id, docker_client)

    sql_text = pkg_resources.resource_string(
        __name__.split('.')[0], 'sql/{}.sql'.format(view_name))
    sql_text_with_partner_short_name = sql_text.replace(
        '[partner_short_name]', partner_short_name)

    export_db.create_view(view_name, sql_text_with_partner_short_name)
