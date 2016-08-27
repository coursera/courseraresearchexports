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

from courseraresearchexports import exports
from datetime import datetime
from requests.exceptions import HTTPError
from tabulate import tabulate
import json
import argparse
import logging
import sys


def download(args):
    """
    Download a data export job using a job id.
    """
    job = exports.api.get(args.id)
    exports.utils.download_export(job, args.dest)


def create(args):
    """
    Create and send an data export request with Coursera.
    """
    export_job_json = exports.utils.build_export_job_json(**vars(args))
    export_job_id = exports.api.create(export_job_json)

    logging.info('Successfully created job %(id)s:\n%(json)s', {
        'id': export_job_id,
        'json': json.dumps(export_job_json, indent=2)
    })


def get(args):
    """
    Get the details and status of a data export request using a job id.
    """
    try:
        export_job = exports.api.get(args.id)
    except HTTPError as err:
        logging.error('Export job %s could not found.\n%s', args.id, err)
        sys.exit(1)

    export_job_info = [['Export Job Id:', args.id]]

    scope_id = exports.utils.get_scope_id_from_job(export_job)
    export_job_info.append(['Scope Id:', scope_id])

    export_type = export_job['exportType']
    export_job_info.append(['Export Type:', export_type])

    creation_time = datetime.fromtimestamp(
        export_job['metadata']['createdAt'] / 1000.0).strftime('%c')
    export_job_info.append(['Created:', creation_time])

    export_job_info.append(['Status:', export_job['status']])

    if export_type == exports.constants.EXPORT_TYPE_SCHEMAS:
        schemas = ', '.join(export_job['schemaNames'])
        export_job_info.append(['Schemas:', schemas])

    if 'downloadLink' in export_job:
        export_job_info.append(['Download Link:', export_job['downloadLink']])

    logging.info('\n' + tabulate(export_job_info, tablefmt="plain"))


def get_all(args):
    """
    Get the details and status of your data export requests.
    """
    try:
        export_jobs = exports.api.get_all()
    except HTTPError as err:
        logging.error('Export jobs couldn\'t be loaded.\n%s', err)
        sys.exit(1)

    export_jobs_table = [['Created', 'Job Id', 'Status', 'Type', 'Scope',
                          'Schemas']]
    for export_job in sorted(export_jobs,
                             key=lambda x: x['metadata']['createdAt'],
                             reverse=True):

        creation_time = datetime.fromtimestamp(
                export_job['metadata']['createdAt']/1000.0
                ).strftime('%Y-%m-%d')

        if export_job['exportType'] == exports.constants.EXPORT_TYPE_EVENTING:
            schemas = 'events'
        elif export_job['exportType'] == \
                exports.constants.EXPORT_TYPE_GRADEBOOK:
            schemas = 'gradebook'
        elif len(export_job['schemaNames']) == \
                len(exports.constants.SCHEMA_NAMES):
            schemas = 'all'
        else:
            schemas = ','.join(export_job['schemaNames'])

        export_jobs_table.append([
            creation_time,
            export_job['id'],
            export_job['status'],
            export_job['exportType'],
            exports.utils.get_scope_id_from_job(export_job),
            schemas])

    logging.info('\n' + tabulate(export_jobs_table, headers='firstrow'))


def parser(subparsers):
    parser_jobs = subparsers.add_parser(
        'jobs',
        help='Get status of current/completed research export job(s)')

    jobs_subparsers = parser_jobs.add_subparsers()

    create_parser(jobs_subparsers)

    parser_get_all = jobs_subparsers.add_parser(
        'getAll',
        help=get_all.__doc__)
    parser_get_all.set_defaults(func=get_all)

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


def create_parser(subparsers):

    parser_create = subparsers.add_parser(
        'create',
        help=create.__doc__)
    parser_create.set_defaults(func=create)
    create_subparsers = parser_create.add_subparsers()

    # common arguments between schema and eventing exports
    create_args_subparser = argparse.ArgumentParser(add_help=False)

    scope_subparser = create_args_subparser.add_mutually_exclusive_group(
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

    create_args_subparser.add_argument(
        '--anonymityLevel',
        choices=exports.constants.ANONYMITY_LEVELS,
        default=exports.constants.ANONYMITY_LEVEL_ISOLATED,
        help='{0} corresponds to data coordinator exports. '
             '{1} has different user id columns in every domain.'.format(
                exports.constants.ANONYMITY_LEVEL_COORDINATOR,
                exports.constants.ANONYMITY_LEVEL_ISOLATED))
    create_args_subparser.add_argument(
        '--statementOfPurpose',
        required=True,
        help='Please let us know how you plan to use the '
             'data, what types of research questions you\'re asking, who will '
             'be working with the data primarily, and with whom you plan to '
             'share it.')

    # schemas subcommand
    parser_schemas = create_subparsers.add_parser(
        'schemas',
        help='Create a data export request from defined schemas.',
        parents=[create_args_subparser])

    parser_schemas.add_argument(
        '--exportType',
        default=exports.constants.EXPORT_TYPE_SCHEMAS,
        help=argparse.SUPPRESS)

    parser_schemas.add_argument(
        '--schemaNames',
        choices=exports.constants.SCHEMA_NAMES,
        nargs='+',
        default=exports.constants.SCHEMA_NAMES,
        help='Data schemas to export. Any combination of: ' +
             ', '.join(exports.constants.SCHEMA_NAMES))

    # eventing subcommand
    parser_eventing = create_subparsers.add_parser(
        'eventing',
        help='Create a data export request for clickstream data.',
        parents=[create_args_subparser])

    parser_eventing.add_argument(
        '--exportType',
        default=exports.constants.EXPORT_TYPE_EVENTING,
        help=argparse.SUPPRESS)

    parser_eventing.add_argument(
        '--interval',
        nargs=2,
        metavar=('START', 'END'),
        help='Interval of {} data to be exported(i.e. 2016-08-01 2016-08-04). '
             'By default this will be the past day.'
             .format(exports.constants.EXPORT_TYPE_EVENTING))

    parser_eventing.add_argument(
        '--ignoreExisting',
        action='store_true',
        help='If flag is set, we will recompute clickstream data for all dates '
             'in the interval. Otherwise, previously computed days are skipped.')