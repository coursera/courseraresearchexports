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
import subprocess

from courseraresearchexports.constants.container_constants import \
    POSTGRES_DOCKER_IMAGE
from courseraresearchexports.models.ContainerInfo import ContainerInfo
from courseraresearchexports.models.ExportDb import ExportDb
from courseraresearchexports.constants.db_constants import \
    HASHED_USER_ID_COLUMN_TO_SOURCE_TABLE


def replace_user_id_placeholders(export_db, sql_text):
    """
    Replace placeholders with actual user_id column names
    :param export_db:
    :param sql_text:
    :return sql_text_with_inferred_columns:
    """
    hashed_user_id_columns_dict = infer_hashed_user_id_columns(export_db)

    for placeholder, column_name in hashed_user_id_columns_dict.items():
        sql_text = sql_text.replace(placeholder, column_name)

    return sql_text


def infer_hashed_user_id_columns(export_db):
    """
    Infer hashed_user_id_columns from database using known placeholders
    :param export_db:
    :return:
    """
    hashed_user_id_columns_dict = {}

    for placeholder, table in HASHED_USER_ID_COLUMN_TO_SOURCE_TABLE.items():
        if table in export_db.tables:
            columns = export_db.get_columns(table)
            inferred_column = infer_user_id_column(columns)
            if inferred_column:
                hashed_user_id_columns_dict[placeholder] = inferred_column

    return hashed_user_id_columns_dict


def infer_user_id_column(columns):
    """
    Infer partner_short_name
    :param columns:
    :return:
    """
    return next((column for column in columns
                 if column.endswith('user_id')), None)


def connect(container_name, docker_client):
    """
    Create psql shell to container databaise
    :param container_name:
    :param docker_client:
    """
    container_info = ContainerInfo.from_container(
        container_name, docker_client)

    subprocess.call([
        'docker', 'run', '-it', '--rm',
        '--link', container_info.name,
        POSTGRES_DOCKER_IMAGE, 'psql',
        '-h', container_info.name,
        '-d', container_info.database_name,
        '-U', 'postgres'
    ], shell=False)


def get_table_names(container_name, docker_client):
    """
    Returns table names present in containerized database.
    :param container_name:
    :param docker_client:
    :return table_names:
    """
    export_db = ExportDb.from_container(container_name, docker_client)

    return export_db.tables


def get_view_names(container_name, docker_client):
    """
    Returns view names present in containerized database.
    :param container_name:
    :param docker_client:
    :return table_names:
    """
    export_db = ExportDb.from_container(container_name, docker_client)

    return export_db.views


def unload_relation(container_name, dest, relation, docker_client):
    """
    Unloads a table or view to a csv file.
    :param container_name:
    :param dest_file:
    :param relation:
    :param docker_client:
    :return:
    """
    if not os.path.exists(dest):
        logging.debug('Creating destination folder: {}'.format(dest))
        os.makedirs(dest)

    export_db = ExportDb.from_container(container_name, docker_client)
    output_filename = os.path.join(dest, '{}.csv'.format(relation))
    rowcount = export_db.unload_relation(relation, output_filename)
    return rowcount


def create_registered_view(container_name, view_name, docker_client):
    """
    Create a prepackaged view
    :param container_name:
    :param view_name:
    :param partner_short_name:
    :param docker_client:
    :return view_name:
    """
    export_db = ExportDb.from_container(container_name, docker_client)

    sql_text = pkg_resources.resource_string(
        __name__.split('.')[0], 'sql/{}.sql'.format(view_name))
    sql_text_with_inferred_columns = replace_user_id_placeholders(
        export_db, sql_text)

    export_db.create_view(view_name, sql_text_with_inferred_columns)

    return view_name


def create_view_from_file(container_name, sql_file, docker_client):
    """
    Create a view from a sql file.
    :param container_name:
    :param sql_file:
    :param partner_short_name:
    :param docker_client:
    :return view_name:
    """
    export_db = ExportDb.from_container(container_name, docker_client)

    with open(sql_file, 'r') as sf:
        sql_text = sf.read()

    view_name = os.path.split(os.path.basename(sql_text))[0]
    sql_text_with_inferred_columns = replace_user_id_placeholders(
        export_db, sql_text)

    export_db.create_view(view_name, sql_text_with_inferred_columns)

    return view_name
