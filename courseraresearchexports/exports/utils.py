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


from courseraresearchexports.exports.api import COURSE_API, SCHEMA_NAMES,\
    EXPORT_TYPES, ANONYMITY_LEVELS
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
    :return:
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
    :return:
    """
    if 'downloadLink' not in export_job:
        logging.error('Export job {} is not ready'.format(export_job['id']))

    if not os.path.exists(dest):
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
    :param course_id:
    :return:
    """
    response = requests.get(requests.compat.urljoin(COURSE_API, course_id))
    response.raise_for_status()
    return response.json()['elements'][0]['slug']


def lookup_course_id_by_slug(course_slug):
    """
    Find the course_id given a course_slug
    :param course_slug:
    :return:
    """
    payload = {'q': 'slug', 'slug': course_slug}
    response = requests.get(COURSE_API, params=payload)
    response.raise_for_status()
    return response.json()['elements'][0]['id']


def create_export_job_json(**kwargs):
    """Creates json body for On Demand Research Exports request.
    Keyword arguments:
    courseID -- Unique identifier for course assigned by Coursera
    courseSlug -- Unique name for course assigned by Coursera
    partnerId -- Identifier for partner institution
    groupId -- Identifier for group
    exportType -- Currently only RESEARCH_WITH_SCHEMAS
    schemaNames -- for RESEARCH_WITH_SCHEMAS datatypes to be exported
    anonymityLevel -- Level of user ID hashing
    statementOfPurpose -- Statement for usage of this export data
    """

    request = {}
    if kwargs.get('courseId'):
        request['scope'] = {
            'typeName': 'courseContext',
            'definition': {
                'courseId': kwargs.get('courseId')
            }
        }
    elif kwargs.get('courseSlug'):
        request['scope'] = {
            'typeName': 'courseContext',
            'definition': {
                'courseId': lookup_course_id_by_slug(kwargs.get('courseSlug'))
            }
        }
    elif kwargs.get('partnerId'):
        request['scope'] = {
            'typeName': 'partnerContext',
            'definition': {
                'partnerId': {
                    'maestroId': kwargs.get('partnerId')
                }
            }
        }
    elif kwargs.get('groupId'):
        request['scope'] = {
            'typeName': 'groupContext',
            'definition': {
                'partnerId': kwargs.get('groupId')
            }
        }
    else:
        raise ValueError('One of courseId, courseSlug, partnerId, '
                         'or groupID must be specified')

    if kwargs.get('exportType'):
        request['exportType'] = kwargs.get('exportType')
        if request['exportType'] == 'RESEARCH_WITH_SCHEMAS':
            if kwargs.get('schemaNames'):
                request['schemaNames'] = kwargs.get('schemaNames')
            else:
                request['schemaNames'] = SCHEMA_NAMES
    else:
        raise ValueError('Export type must be in [{}]'.format(
            ', '.join(EXPORT_TYPES)))

    if kwargs.get('anonymityLevel'):
        request['anonymityLevel'] = kwargs.get('anonymityLevel')
    else:
        raise ValueError('Anonymity levels must be in [{}]'.format(
            ', '.join(ANONYMITY_LEVELS)))

    if kwargs.get('statementOfPurpose'):
        request['statementOfPurpose'] = kwargs.get('statementOfPurpose')
    else:
        raise ValueError('Statement of purpose must be specified')

    return request
