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


from courseraresearchexports.exports.constants import COURSE_API, PARTNER_API,\
    EXPORT_TYPE_EVENTING, EXPORT_TYPE_SCHEMAS
from urlparse import urlparse
from tqdm import tqdm
import requests
import os
import logging
import zipfile


def extract_export_archive(export_archive, dest, delete_archive=True):
    """
    Extracts a compressed folder
    :param export_archive:
    :param dest:
    :param delete_archive: delete the archive after extracting
    :return dest:
    """
    try:
        with zipfile.ZipFile(export_archive, 'r') as z:
            z.extractall(dest)
        if delete_archive:
            os.remove(export_archive)
        return dest
    except:
        logging.error('Error in extracting export archive {} to {}'.format(
            export_archive, dest))
        raise


def download_export(export_job, dest):
    """
    Download an export archive if ready given an export_job_id
    :param export_job:
    :param dest:
    :return output_filename:
    """
    if export_job['exportType'] == EXPORT_TYPE_EVENTING:
        logging.error('Generate download links to download eventing exports')
        raise ValueError('Require {} job'.format(EXPORT_TYPE_SCHEMAS))
    elif 'downloadLink' not in export_job:
        logging.error('Export job {} is not ready'.format(export_job['id']))
        raise ValueError('Export job is not yet ready for download')

    if not os.path.exists(dest):
        logging.debug('Creating destination {}'.format(dest))
        os.makedirs(dest)
    download_link = export_job['downloadLink']
    export_filename = urlparse(download_link).path.split('/')[-1]
    response = requests.get(download_link, stream=True)
    chunk_size = 1024 * 1024
    output_filename = os.path.join(dest, export_filename)

    with open(output_filename, 'wb') as f:
        for data in tqdm(
                iterable=response.iter_content(chunk_size),
                total=int(response.headers['Content-length'])/chunk_size,
                unit='MB',
                desc=export_filename):

            f.write(data)

    return output_filename


def lookup_course_slug_by_id(course_id):
    """
    Find the course slug given an course_id
    """
    response = requests.get(requests.compat.urljoin(COURSE_API, course_id))
    response.raise_for_status()
    return response.json()['elements'][0]['slug']


def lookup_course_id_by_slug(course_slug):
    """
    Find the course_id given a course_slug
    """
    payload = {'q': 'slug', 'slug': course_slug}
    response = requests.get(COURSE_API, params=payload)
    response.raise_for_status()
    return response.json()['elements'][0]['id']


def lookup_partner_id_by_short_name(partner_short_name):
    """
    Find the partner_id by short name
    """
    payload = {'q': 'shortName', 'shortName': partner_short_name}
    response = requests.get(COURSE_API, params=payload)
    response.raise_for_status()
    return response.json()['elements'][0]['id']


def lookup_partner_short_name_by_id(partner_id):
    """
    Find the partner_id by short name
    """
    response = requests.get(requests.compat.urljoin(PARTNER_API, partner_id))
    response.raise_for_status()
    return response.json()['elements'][0]['slug']


def get_scope_id_from_job(export_job):
    """
    Find the course/partner/group id from an export job
    :param export_job:
    :return scope_id:
    """
    job_scope = export_job['scope']
    if job_scope['typeName'] == 'courseContext':
        scope_id = job_scope['definition']['courseId']
    elif job_scope['typeName'] == 'partnerContext':
        scope_id = job_scope['definition']['partnerId']['maestroId']
    elif job_scope['typeName'] == 'groupContext':
        scope_id = job_scope['definition']['groupId']
    else:
        scope_id = 'unknown'

    return scope_id


def remove_empty_fields(request):
    "Remove fields that are None"
    return {field: value for (field, value) in request.items() if value}


def build_export_job_json(**kwargs):
    """Creates json body for On Demand Research Exports request. No validation
    is performed on the fields.
    Keyword arguments:
    courseID -- Unique identifier for course assigned by Coursera
    courseSlug -- Unique name for course assigned by Coursera
    partnerId -- Identifier for partner institution
    partnerShortName -- Identifier for partner institution
    groupId -- Identifier for group
    exportType -- Type of research export
    schemaNames -- for schema tables export
    interval -- dates to export when exporting RESEARCH_EVENTING
    anonymityLevel -- Level of user ID hashing
    statementOfPurpose -- Statement for usage of this export data
    """

    request = {}
    if kwargs.get('courseId'):
        request['scope'] = {
            'typeName': 'courseContext',
            'definition': {
                'courseId': kwargs['courseId']
            }}
    elif kwargs.get('courseSlug'):
        request['scope'] = {
            'typeName': 'courseContext',
            'definition': {
                'courseId': lookup_course_id_by_slug(kwargs['courseSlug'])
            }}
    elif kwargs.get('partnerId'):
        request['scope'] = {
            'typeName': 'partnerContext',
            'definition': {
                'partnerId': {
                    'maestroId': kwargs['partnerId']
                }}}
    elif kwargs.get('partnerShortName'):
        request['scope'] = {
            'typeName': 'partnerContext',
            'definition': {
                'partnerId': {
                    'maestroId': lookup_partner_id_by_short_name(
                        kwargs['partnerShortName'])
                }}}
    elif kwargs.get('groupId'):
        request['scope'] = {
            'typeName': 'groupContext',
            'definition': {
                'groupId': kwargs['groupId']
            }}

    request['exportType'] = kwargs.get('exportType')
    request['schemaNames'] = kwargs.get('schemaNames')
    request['anonymityLevel'] = kwargs.get('anonymityLevel')
    request['ignoreExisting'] = kwargs.get('ignoreExisting')
    request['interval'] = kwargs.get('interval')
    request['statementOfPurpose'] = kwargs.get('statementOfPurpose')

    return remove_empty_fields(request)
