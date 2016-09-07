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
from sqlalchemy.engine import reflection

import csv
import logging


class ExportDb:
    """
    Interface to SQLAlchemy for interacting with the a database
    on a docker container
    """
    def __init__(self, host_ip=None, host_port=None, db=None, **kwargs):

        if not (host_ip and host_port and db):
            raise ValueError(
                'Host IP, port and database name must be specified')

        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

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
    def from_container_info(cls, container_info):
        return cls(host_ip=container_info.host_ip,
                   host_port=container_info.host_port,
                   db=container_info.database_name)

    def create_view(self, name, sql_text):
        view_statement = """
        DROP VIEW IF EXISTS {name};
        CREATE VIEW {name} AS {sql_text};
        """.format(name=name, sql_text=sql_text)

        self.engine.execute(view_statement)

    def unload(self, dest_file, sql_text):
        result = self.engine.execute(sql_text)

        with open(dest_file, 'wb') as csv_file:
            csv_obj = csv.writer(csv_file)

            csv_obj.writerow(result.keys())
            for row in result:
                encoded_row = [col.encode('utf8')
                               if isinstance(col, unicode) else col
                               for col in row]
                csv_obj.writerow(encoded_row)

    def unload_relation(self, dest_file, relation):
        query = 'SELECT * FROM {relation};'.format(relation=relation)
        self.unload(dest_file, sql_text=query)

    @property
    def tables(self):
        insp = reflection.Inspector.from_engine(self.engine)
        return insp.get_table_names()

    @property
    def views(self):
        insp = reflection.Inspector.from_engine(self.engine)
        return insp.get_view_names()