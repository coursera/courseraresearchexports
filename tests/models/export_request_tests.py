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

from courseraresearchexports.constants.api_constants import SCHEMA_NAMES, \
    EXPORT_TYPE_TABLES, EXPORT_TYPE_CLICKSTREAM, EXPORT_TYPE_GRADEBOOK
from courseraresearchexports.models.ExportRequest import ExportRequest
from courseraresearchexports.models.ExportRequestWithMetadata import \
    ExportRequestWithMetadata
from mock import patch

fake_course_id = 'fake_course_id'
fake_course_slug = 'fake_course'
fake_partner_id = 'fake_partner_id'
fake_partner_short_name = 'fake_partner'
fake_export_id = '1'


def test_export_request_serialize_to_json():
    export_request = ExportRequest(course_id=fake_course_id)
    expected_result = {
        'scope': {
            'typeName': 'courseContext',
            'definition': {
                'courseId': fake_course_id}}}

    assert export_request.to_json() == expected_result


def test_export_request_deserialize_from_json():
    export_request_json = {
        'scope': {
            'typeName': 'courseContext',
            'definition': {
                'courseId': fake_course_id}}}
    export_request = ExportRequest.from_json(export_request_json)

    assert ExportRequest(course_id=fake_course_id) == export_request


def test_create_from_args():
    export_request = ExportRequest.from_args(course_id=fake_course_id)
    assert ExportRequest(course_id=fake_course_id) == export_request


@patch('courseraresearchexports.utils.export_utils.lookup_course_id_by_slug')
def test_course_id_inference(lookup_course_id_by_slug):
    lookup_course_id_by_slug.return_value = fake_course_id
    export_request = ExportRequest.from_args(course_slug=fake_course_slug)

    assert ExportRequest(course_id=fake_course_id) == export_request


@patch('courseraresearchexports.utils.export_utils.'
       'lookup_partner_id_by_short_name')
def test_partner_id_inference(lookup_partner_id_by_short_name):
    lookup_partner_id_by_short_name.return_value = fake_partner_id
    export_request = ExportRequest.from_args(
        partner_short_name=fake_partner_short_name)

    assert ExportRequest(partner_id=fake_partner_id) == export_request


def test_scope_id():
    export_request = ExportRequest(course_id=fake_course_id)

    assert export_request.scope_id == fake_course_id


def test_schemas():
    eventing_request = ExportRequest(
        course_id=fake_course_id, export_type=EXPORT_TYPE_CLICKSTREAM)
    gradebook_request = ExportRequest(
        course_id=fake_course_id, export_type=EXPORT_TYPE_GRADEBOOK)
    all_tables_request = ExportRequest(
        course_id=fake_course_id, export_type=EXPORT_TYPE_TABLES,
        schema_names=SCHEMA_NAMES)

    assert eventing_request.schema_names_display is None
    assert gradebook_request.schema_names_display is None
    assert all_tables_request.schema_names_display == 'all'


def test_export_request_with_metadata_from_export_request():
    export_request = ExportRequest.from_args(course_id=fake_course_id)
    export_request_with_metadata = \
        ExportRequestWithMetadata.from_export_request(
            export_request, id=fake_export_id)

    assert export_request.course_id == export_request_with_metadata.course_id


def test_export_request_with_metadata_serialize_to_json():
    export_request = ExportRequestWithMetadata(course_id=fake_course_id,
                                               id=fake_export_id)
    expected_result = {
        'scope': {
            'typeName': 'courseContext',
            'definition': {
                'courseId': fake_course_id}},
        'id': fake_export_id}

    assert export_request.to_json() == expected_result


def test_export_request_with_metadata_deserialize_from_json():
    export_request_json = {
        'scope': {
            'typeName': 'courseContext',
            'definition': {
                'courseId': fake_course_id}},
        'id': fake_export_id}
    export_request = ExportRequestWithMetadata.from_json(export_request_json)

    assert export_request == ExportRequestWithMetadata(
                                course_id=fake_course_id, id=fake_export_id)
