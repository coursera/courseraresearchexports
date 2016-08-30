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

from courseraresearchexports.exports import utils
from courseraresearchexports.exports.constants import EXPORT_TYPE_EVENTING, \
    EXPORT_TYPE_GRADEBOOK, SCHEMA_NAMES, EXPORT_TYPE_SCHEMAS
from datetime import datetime
from tqdm import tqdm
from urlparse import urlparse
import logging
import os
import requests
import time


class ExportRequest:
    """
    Represents a export request for Coursera's research data export
    service and provides methods for serialization.
    """

    def __init__(self, course_id=None, partner_id=None, group_id=None,
                 export_type=None, anonymity_level=None,
                 statement_of_purpose=None, schema_names=None,
                 interval=None, ignore_existing=None, **kwargs):
        self.course_id = course_id
        self.partner_id = partner_id
        self.group_id = group_id
        self.export_type = export_type
        self.anonymity_level = anonymity_level
        self.statement_of_purpose = statement_of_purpose
        self.schema_names = schema_names
        self.interval = interval
        self.ignore_existing = ignore_existing

    def to_json(self):
        """
        Serialize ExportRequest to a dictionary representing a json object.
        No validation is done with the exception that only specification of
        scope is used (course/partner/group).
        :return json_request:
        """
        json_request = {}

        if self.course_id:
            json_request['scope'] = {
                'typeName': 'courseContext',
                'definition': {
                    'courseId': self.course_id
                }}
        elif self.partner_id:
            json_request['scope'] = {
                'typeName': 'partnerContext',
                'definition': {
                    'partnerId': {
                        'maestroId': self.partner_id
                    }}}
        elif self.group_id:
            json_request['scope'] = {
                'typeName': 'groupContext',
                'definition': {
                    'groupId': self.group_id
                }}
        if self.export_type:
            json_request['exportType'] = self.export_type
        if self.anonymity_level:
            json_request['anonymityLevel'] = self.anonymity_level
        if self.statement_of_purpose:
            json_request['statementOfPurpose'] = self.statement_of_purpose
        if self.schema_names:
            json_request['schemaNames'] = self.schema_names
        if self.interval:
            json_request['interval'] = self.interval
        if self.ignore_existing:
            json_request['ignoreExisting'] = self.ignore_existing

        return json_request

    @staticmethod
    def from_args(**kwargs):
        """
        Create a ExportResource object using the parameters required. Performs
        course_id/partner_id inference if possible.
        :param kwargs:
        :return export_request: ExportRequest
        """
        if kwargs.get('course_slug') and not kwargs.get('course_id'):
            kwargs['course_id'] = utils.lookup_course_id_by_slug(
                kwargs['course_slug'])
        elif kwargs.get('partner_short_name') and not kwargs.get('partner_id'):
            kwargs['partner_id'] = utils.lookup_partner_id_by_short_name(
                kwargs['partner_short_name'])

        return ExportRequest(**kwargs)

    @staticmethod
    def from_json(json_request):
        """
        Deserialize ExportRequest from json object.
        :param json_request:
        :return export_request: ExportRequest
        """
        kwargs = {}
        request_scope = json_request['scope']
        request_scope_context = request_scope['typeName']

        if request_scope_context == 'courseContext':
            kwargs['course_id'] = request_scope['definition']['courseId']
        elif request_scope_context == 'partnerContext':
            kwargs['partner_id'] = \
                request_scope['definition']['partnerId']['maestroId']
        elif request_scope_context == 'groupContext':
            kwargs['group_id'] = request_scope['definition']['groupId']

        return ExportRequest(
            export_type=json_request.get('exportType'),
            anonymity_level=json_request.get('anonymityLevel'),
            statement_of_purpose=json_request.get('statementOfPurpose'),
            schema_names=json_request.get('schemaNames'),
            interval=json_request.get('interval'),
            ignore_existing=json_request.get('ignoreExisting'),
            **kwargs)

    @property
    def scope_id(self):
        """
        Identifier for the scope, assume that only one of course/partner/group
        is defined for a valid request.
        :return scope_id:
        """
        return self.course_id or self.partner_id or self.group_id

    @property
    def schemas(self):
        """
        String representation of schemas to be returned in export request.
        :return schemas:
        """
        if self.export_type == EXPORT_TYPE_EVENTING:
            return 'events'
        elif self.export_type == EXPORT_TYPE_GRADEBOOK:
            return 'gradebook'
        elif set(self.schema_names) == set(SCHEMA_NAMES):
            return 'all'
        else:
            return ','.join(self.schema_names)


class ExportRequestMetadata:
    """Metadata about the internal timings of the export request"""

    def __init__(self, created_by=None, created_at=None, started_at=None,
                 completed_at=None, snapshot_at=None, **kwargs):
        self.created_by = created_by
        self.created_at = created_at
        self.started_at = started_at
        self.completed_at = completed_at
        self.snapshot_at = snapshot_at

    def to_json(self):
        """
        Serialize metadata from json object.
        :return json_metadata:
        """
        json_metadata = {}
        if self.created_by:
            json_metadata['createdBy'] = self.created_by
        if self.created_at:
            json_metadata['createdAt'] = datetime_to_ts(self.created_at)
        if self.started_at:
            json_metadata['startedAt'] = datetime_to_ts(self.started_at)
        if self.completed_at:
            json_metadata['completedAt'] = datetime_to_ts(self.completed_at)
        if self.snapshot_at:
            json_metadata['snapshotAt'] = datetime_to_ts(self.snapshot_at)

        return json_metadata

    @staticmethod
    def from_json(json_metadata):
        """
        Deserialize ExportRequestMetaData from json object.
        :param json_metadata:
        :return export_request_metadata: ExportRequestMetadata
        """
        kwargs = {}
        if json_metadata.get('createdBy'):
            kwargs['created_by'] = json_metadata['createdBy']
        if json_metadata.get('createdAt'):
            kwargs['created_at'] = timestamp_to_dt(json_metadata['createdAt'])
        if json_metadata.get('completedAt'):
            kwargs['completed_at'] = timestamp_to_dt(
                json_metadata['completedAt'])
        if json_metadata.get('startedAt'):
            kwargs['started_at'] = timestamp_to_dt(json_metadata['startedAt'])
        if json_metadata.get('snapshotAt'):
            kwargs['snapshot_at'] = timestamp_to_dt(
                json_metadata['snapshotAt'])
        return ExportRequestMetadata(**kwargs)


class ExportRequestWithMetadata(ExportRequest):
    """
    Class representing a export request from Coursera's research data export
    service with metadata about its status.
    """

    def __init__(self, course_id=None, partner_id=None, group_id=None,
                 export_type=None, anonymity_level=None,
                 statement_of_purpose=None, schema_names=None,
                 interval=None, ignore_existing=None, id=None,
                 status=None, download_link=None, metadata=None, **kwargs):
        ExportRequest.__init__(
            self, course_id=course_id, partner_id=partner_id,
            group_id=group_id, export_type=export_type,
            anonymity_level=anonymity_level,
            statement_of_purpose=statement_of_purpose,
            schema_names=schema_names, interval=interval,
            ignore_existing=ignore_existing)
        self.id = id
        self.status = status
        self.download_link = download_link
        self.metadata = metadata

    def to_json(self):
        """
        Serialize ExportRequestWithMetadata to json object
        :return json_request:
        """
        json_request = ExportRequest.to_json(self)

        if self.id:
            json_request['id'] = self.id
        if self.status:
            json_request['status'] = self.status
        if self.download_link:
            json_request['downloadLink'] = self.download_link
        if self.metadata:
            json_request['metadata'] = self.metadata.to_json()

        return json_request

    @staticmethod
    def from_json(json_request):
        """
        Deserialize ExportRequest from json object.
        :param json_request:
        :return export_request: ExportRequestWithMetadata
        """
        kwargs = {}
        request_scope = json_request['scope']
        request_scope_context = request_scope['typeName']

        if request_scope_context == 'courseContext':
            kwargs['course_id'] = request_scope['definition']['courseId']
        elif request_scope_context == 'partnerContext':
            kwargs['partner_id'] = \
                request_scope['definition']['partnerId']['maestroId']
        elif request_scope_context == 'groupContext':
            kwargs['group_id'] = request_scope['definition']['groupId']

        return ExportRequestWithMetadata(
            export_type=json_request.get('exportType'),
            anonymity_level=json_request.get('anonymityLevel'),
            statement_of_purpose=json_request.get('statementOfPurpose'),
            schema_names=json_request.get('schemaNames'),
            interval=json_request.get('interval'),
            ignore_existing=json_request.get('ignoreExisting'),
            id=json_request.get('id'),
            status=json_request.get('status'),
            download_link=json_request.get('downloadLink'),
            metadata=ExportRequestMetadata.from_json(
                json_request.get('metadata')),
            **kwargs)

    @property
    def created_at(self):
        return self.metadata.created_at

    def download(self, dest):
        """
        Download an export archive associated with this export request
        :param dest:
        :return output_filename:
        """
        if self.export_type == EXPORT_TYPE_EVENTING:
            logging.error(
                'Generate download links to access eventing export requests'
                'using `courseraresearchexports jobs eventing_download_links`.'
                ' Please refer to the Coursera Export Guide for details'
                'https://coursera.gitbooks.io/data-exports/content/'
                'introduction/programmatic_access.html')
            raise ValueError(
                'Require export_type = {}'.format(EXPORT_TYPE_SCHEMAS))
        elif not self.download_link:
            if self.status in ['PENDING', 'IN_PROGRESS']:
                logging.error(
                    'Export request {} is currently {} and is not ready for'
                    'download. Please wait until the request is completed.'
                    .format(self.id, self.status))
                raise ValueError(
                    'Export request is not yet ready for download')
            elif self.status == 'TERMINATED':
                logging.error(
                    'Export request has been TERMINATED. Please contact '
                    'data-support@coursera.org if we have not resolved this '
                    'within 24 hours.')
                raise ValueError('Export request has been TERMINATED')
            else:
                logging.error('Download link was not found.')
                raise ValueError('Download link was not found')

        if not os.path.exists(dest):
            logging.debug('Creating destination folder: {}'.format(dest))
            os.makedirs(dest)

        export_filename = urlparse(self.download_link).path.split('/')[-1]
        response = requests.get(self.download_link, stream=True)
        chunk_size = 1024 * 1024
        output_filename = os.path.join(dest, export_filename)
        logging.debug('Writing to file: {}'.format(output_filename))

        with open(output_filename, 'wb') as f:
            for data in tqdm(
                    iterable=response.iter_content(chunk_size),
                    total=int(response.headers['Content-length']) / chunk_size,
                    unit='MB',
                    desc=export_filename):
                f.write(data)

        return output_filename


def datetime_to_ts(dt):
    """Convert datetime object to timestamp in milliseconds"""
    return int(time.mktime(dt.timetuple()) * 1000)


def timestamp_to_dt(ts):
    """Convert timestamp in milliseconds to datetime object"""
    return datetime.fromtimestamp(ts / 1000.0)
