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

import csv

from sqlalchemy import create_engine
from sqlalchemy.engine import reflection

from courseraresearchexports.models.ContainerInfo import ContainerInfo


class ExportDb:
    """
    Interface to SQLAlchemy for interacting with the a database
    on a docker container
    """
    def __init__(self, host_ip=None, host_port=None, db=None, **kwargs):

        if not (host_ip and host_port and db):
            raise ValueError(
                'Host IP, port and database name must be specified')

        self.host_ip = host_ip
        self.host_port = host_port
        self.db = db
        self.engine = create_engine(
            "postgresql://{user}@{host}:{port}/{db}"
            .format(user='postgres',
                    host=self.host_ip,
                    port=self.host_port,
                    db=self.db))

    @classmethod
    def from_container(cls, container_name_or_id, docker_client):
        """
        Create ExportDb object directly from container_name_or_id identifier.
        :param container_name_or_id:
        :param docker_client:
        :return:
        """
        container_info = ContainerInfo.from_container(container_name_or_id,
                                                      docker_client)
        return cls.from_container_info(container_info)

    @classmethod
    def from_container_info(cls, container_info):
        """
        Create an ExportDb object from the information about a container
        :param container_info: ContainerInfo
        :return export_db: ExportDb
        """
        return cls(host_ip=container_info.host_ip,
                   host_port=container_info.host_port,
                   db=container_info.database_name)

    def create_view(self, name, sql_text):
        """
        Creates or overrides an existing view given a select statement.
        :param name:
        :param sql_text:
        :return:
        """
        view_statement = """
        DROP VIEW IF EXISTS {name};
        CREATE VIEW {name} AS {sql_text};
        """.format(name=name, sql_text=sql_text)

        self.engine.execute(view_statement)

    def unload(self, query, output_filename):
        """
        Unloads to a csv file given a query.
        :param query:
        :param output_filename:
        :return:
        """
        result = self.engine.execute(query)

        with open(output_filename, 'wb') as csv_file:
            csv_obj = csv.writer(csv_file)
            csv_obj.writerow(result.keys())
            for row in result:
                encoded_row = [col.encode('utf8')
                               if isinstance(col, unicode) else col
                               for col in row]
                csv_obj.writerow(encoded_row)

    def unload_relation(self, relation, output_filename):
        """
        Unload a table or view.
        :param relation:
        :param output_filename:
        :return:
        """
        query = 'SELECT * FROM {relation};'.format(relation=relation)
        self.unload(query, output_filename)

    @property
    def tables(self):
        """
        Names of all tables present on database.
        """
        insp = reflection.Inspector.from_engine(self.engine)
        return insp.get_table_names()

    @property
    def views(self):
        """
        Names of all views present on database.
        """
        insp = reflection.Inspector.from_engine(self.engine)
        return insp.get_view_names()