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

from courseraoauth2client import oauth2

import courseraresearchexports.exports.constants
from courseraresearchexports.exports import api
from courseraresearchexports.exports import utils
from datetime import datetime
import requests
import json
import argparse
import logging


def download(args):
    """
    Download research export job using a job id.
    """
    job = api.get(args.id)
    utils.download_export(job, args.dest)


def create(args):
    """
    Creates a post request to Coursera's research exports service
     with specified parameters
    """
    export_job_json = utils.create_export_job_json(**vars(args))
    export_job_id = api.create(export_job_json)

    print('Successfully created job {}:\n{}'.format(
        export_job_id,
        json.dumps(export_job_json, indent=2)))


def get(args):
    """
    Get status of a research export job using a job id.
    """
    job = api.get(args.id)

    scope_id, scope_name = utils.get_scope_id_and_name_from_job(job)

    export_type = job['exportType']

    if export_type == 'RESEARCH_WITH_SCHEMAS':
        schemas_str = 'Schemas: ' + ', '.join(job['schemaNames']) + '\n'
    else:
        schemas_str = ''

    creation_time = datetime.fromtimestamp(
            job['metadata']['createdAt']/1000.0).strftime('%c')

    download_link = job['downloadLink'] if 'downloadLink' in job else None

    job_str = 'Job id: {}\nScope id: {}\nScope name: {}\nType: {}\n' \
              'Created: {}\nStatus: {}\n{}Download Link: {}'

    print(job_str.format(
        job['id'],
        scope_id,
        scope_name,
        job['exportType'],
        creation_time,
        job['status'],
        schemas_str,
        download_link))


def get_all(args):
    """
    Get status of all research export jobs that you have requested.
    """
    export_jobs = api.get_all()

    # print out jobs by creation date
    template = "{0:12}{1:12}{2:10}{3:25}{4:12}{5:18}"
    print(template.format("Time", "ExportID", "Type",
                          "Scope", "Status", "Schemas"))
    for job in sorted(
            export_jobs,
            key=lambda x: x['metadata']['createdAt'],
            reverse=True):

        creation_time = datetime.fromtimestamp(
            job['metadata']['createdAt']/1000.0).strftime('%Y-%m-%d')

        if job['exportType'] == 'RESEARCH_EVENTING':
            schema_names = 'events'
        elif len(job['schemaNames']) == len(
                courseraresearchexports.exports.constants.SCHEMA_NAMES):
            schema_names = 'all'
        else:
            schema_names = ','.join(job['schemaNames'])

        if job['exportType'] == 'RESEARCH_WITH_SCHEMAS':
            export_type = 'schemas'
        else:
            export_type = 'eventing'

        _, scope_name = utils.get_scope_id_and_name_from_job(job)

        print(template.format(
            creation_time,
            job['id'],
            export_type,
            scope_name,
            job['status'],
            schema_names))


def parser(subparsers):
    parser_jobs = subparsers.add_parser(
        'jobs',
        help='Get status of current/completed research export job(s)')

    jobs_subparsers = parser_jobs.add_subparsers()

    create_subparser = argparse.ArgumentParser(add_help=False)
    scope_subparser = create_subparser.add_mutually_exclusive_group(
        required=True)
    scope_subparser.add_argument(
        '--courseId',
        help='Export rows corresponding to learners within a course '
        'according to the unique id assigned by Coursera.')
    scope_subparser.add_argument(
        '--courseSlug',
        help='Export rows corresponding to learners within a course '
        'according to the unique name of your course defined as '
        'the part after /learn in the course url. (e.g. machine-'
        'learning for https://www.coursera.org/learn/machine-learning)')
    scope_subparser.add_argument(
        '--partnerId',
        help='Export rows corresponding to learners within a partner')
    scope_subparser.add_argument(
        '--partnerShortName',
        help='Export rows corresponding to learners within a partner')
    scope_subparser.add_argument(
        '--groupId',
        help='Export rows corresponding to learners without a group')
    create_subparser.add_argument(
        '--exportType',
        choices=courseraresearchexports.exports.constants.EXPORT_TYPES,
        default=courseraresearchexports.exports.constants.EXPORT_TYPES[0],
        help='Course data is provided with RESEARCH_WITH_SCHEMAS and '
        'clickstream data is exported with RESEARCH_EVENTING.'
        'schemaNames must be specified for RESEARCH_WITH_SCHEMAS and '
        'interval must be specified for RESEARCH_EVENTING')
    create_subparser.add_argument(
        '--schemaNames',
        choices=courseraresearchexports.exports.constants.SCHEMA_NAMES,
        nargs='+',
        default=courseraresearchexports.exports.constants.SCHEMA_NAMES,
        help='Data types to be exported. Any combination of: ' +
        ', '.join(courseraresearchexports.exports.constants.SCHEMA_NAMES))
    create_subparser.add_argument(
        '--interval',
        nargs=2,
        metavar=('START', 'END'),
        help='Interval of RESEARCH_EVENTING data to be expordtd '
        '(i.e. 2016-08-01 2016-08-04)')
    create_subparser.add_argument(
        '--anonymityLevel',
        choices=courseraresearchexports.exports.constants.ANONYMITY_LEVELS,
        default=courseraresearchexports.exports.constants.ANONYMITY_LEVELS[0],
        help='One of HASHED_IDS_NO_PII or HASHED_IDS_WITH_ISOLATED_UGC_NO_PII.'
        ' If you are a data coordinator, you may request HASHED_IDS_NO_PII')
    create_subparser.add_argument(
        '--statementOfPurpose',
        required=True,
        help='To help us scale our research efforts and provide you with '
        'better data tools, please let us know how you plan to use the data, '
        'what types of research questions you\'re asking, who will be working '
        'with the data primarily, and with whom you plan to share it.')
    create_subparser.add_argument(
        '--ignoreExisting',
        action='store_true',
        help='If flag is set, we will recompute clickstream data all dates in '
        'interval. Otherwise, if the selected interval consists of days that '
        'we have previously computed clickstream data for, we skip these days')
    parser_create = jobs_subparsers.add_parser(
        'create',
        help=create.__doc__,
        parents=[create_subparser])
    parser_create.set_defaults(func=create)

    parser_getAll = jobs_subparsers.add_parser(
        'getAll',
        help=get_all.__doc__)
    parser_getAll.set_defaults(func=get_all)

    parser_get = jobs_subparsers.add_parser(
        'get',
        help=get.__doc__)
    parser_get.set_defaults(func=get)

    parser_get.add_argument(
        'id',
        help='Export job ID')

    parser_download = jobs_subparsers.add_parser(
        'download',
        help=download.__doc__)
    parser_download.set_defaults(func=download)

    parser_download.add_argument(
        'id',
        help='Export job ID')

    parser_download.add_argument(
        '--dest',
        default='.',
        help='Destination folder')

    return parser_jobs
