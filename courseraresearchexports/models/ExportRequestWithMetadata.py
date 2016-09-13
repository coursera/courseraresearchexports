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
import time

from courseraresearchexports.models.ExportRequest import ExportRequest


class ExportRequestMetadata:
    """Metadata about the internal timings of the export request"""

    def __init__(self, created_by=None, created_at=None, started_at=None,
                 completed_at=None, snapshot_at=None, **kwargs):
        self._created_by = created_by
        self._created_at = created_at
        self._started_at = started_at
        self._completed_at = completed_at
        self._snapshot_at = snapshot_at

    def to_json(self):
        """
        Serialize metadata from json object.
        :return json_metadata:
        """
        json_metadata = {}
        if self._created_by:
            json_metadata['createdBy'] = self._created_by
        if self._created_at:
            json_metadata['createdAt'] = datetime_to_unix_ms(self._created_at)
        if self._started_at:
            json_metadata['startedAt'] = datetime_to_unix_ms(self._started_at)
        if self._completed_at:
            json_metadata['completedAt'] = datetime_to_unix_ms(
                self._completed_at)
        if self._snapshot_at:
            json_metadata['snapshotAt'] = datetime_to_unix_ms(
                self._snapshot_at)

        return json_metadata

    @classmethod
    def from_json(cls, json_metadata):
        """
        Deserialize ExportRequestMetaData from json object.
        :param json_metadata:
        :return export_request_metadata: ExportRequestMetadata
        """
        if json_metadata:
            kwargs = {}
            if json_metadata.get('createdBy'):
                kwargs['created_by'] = json_metadata['createdBy']
            if json_metadata.get('createdAt'):
                kwargs['created_at'] = unix_ms_to_datetime(
                    json_metadata['createdAt'])
            if json_metadata.get('completedAt'):
                kwargs['completed_at'] = unix_ms_to_datetime(
                    json_metadata['completedAt'])
            if json_metadata.get('startedAt'):
                kwargs['started_at'] = unix_ms_to_datetime(
                    json_metadata['startedAt'])
            if json_metadata.get('snapshotAt'):
                kwargs['snapshot_at'] = unix_ms_to_datetime(
                    json_metadata['snapshotAt'])
            return cls(**kwargs)

        else:
            return None


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
        self._id = id
        self._status = status
        self._download_link = download_link
        self._metadata = metadata

    def to_json(self):
        """
        Serialize ExportRequestWithMetadata to json object
        :return json_request:
        """
        json_request = ExportRequest.to_json(self)

        if self._id:
            json_request['id'] = self._id
        if self._status:
            json_request['status'] = self._status
        if self._download_link:
            json_request['downloadLink'] = self._download_link
        if self._metadata:
            json_request['metadata'] = self._metadata.to_json()

        return json_request

    @classmethod
    def from_export_request(cls, export_request, id=None, status=None,
                            download_link=None, metadata=None, **kwargs):
        """
        Create an object of class ExportRequestWithMetadata from an object of
        class ExportRequest.
        :param export_request: ExportRequest, parent object
        :param id:
        :param status:
        :param download_link:
        :param metadata:
        :param kwargs:
        :return export_request_with_metadata: ExportRequestWithMetadata
        """
        return cls(
            course_id=export_request._course_id,
            partner_id=export_request._partner_id,
            group_id=export_request._group_id,
            export_type=export_request._export_type,
            anonymity_level=export_request._anonymity_level,
            statement_of_purpose=export_request._statement_of_purpose,
            schema_names=export_request._schema_names,
            interval=export_request._interval,
            ignore_existing=export_request._ignore_existing,
            id=id,
            status=status,
            download_link=download_link,
            metadata=metadata)

    @classmethod
    def from_json(cls, json_request):
        """
        Deserialize ExportRequestWithMetadata from json object.
        :param json_request:
        :return export_request: ExportRequestWithMetadata
        """
        export_request = ExportRequest.from_json(json_request)

        return cls.from_export_request(
            export_request=export_request,
            id=json_request.get('id'),
            status=json_request.get('status'),
            download_link=json_request.get('downloadLink'),
            metadata=ExportRequestMetadata.from_json(
                json_request.get('metadata')))

    @classmethod
    def from_response(cls, response):
        """
        Instantiate a list of ExportRequestWithMeta objects from
        API call response.
        :param response:
        :return export_request_with_metadata_list: [ExportRequestWithMetadata]
        """
        return [cls.from_json(export_request)
                for export_request in response.json()['elements']]

    @property
    def id(self):
        return self._id

    @property
    def status(self):
        return self._status

    @property
    def download_link(self):
        return self._download_link

    @property
    def metadata(self):
        return self._metadata

    @property
    def created_at(self):
        if self._metadata and self._metadata._created_at:
            return self._metadata._created_at
        else:
            return datetime.fromtimestamp(0)


def datetime_to_unix_ms(dt):
    """Convert datetime object to timestamp in milliseconds"""
    return int(time.mktime(dt.timetuple()) * 1000)


def unix_ms_to_datetime(unix_ms):
    """Convert timestamp in milliseconds to datetime object"""
    return datetime.fromtimestamp(unix_ms / 1000.0)
