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

from tabulate import tabulate
import json
import argparse
import logging

from courseraresearchexports import exports
from courseraresearchexports.models.ClickstreamDownloadLinksRequest import \
    ClickstreamDownloadLinksRequest
from courseraresearchexports.models.ExportRequest import ExportRequest


def request(args):
    """
    Create and send an data export request with Coursera.
    """
    if args.export_type == exports.constants.EXPORT_TYPE_TABLES:
        export_request = ExportRequest.from_args(
            course_id=args.course_id,
            course_slug=args.course_slug,
            partner_id=args.partner_id,
            parter_short_name=args.partner_short_name,
            group_id=args.group_id,
            export_type=args.export_type,
            anonymity_level=args.anonymity_level,
            statement_of_purpose=args.statement_of_purpose,
            schema_names=args.schema_names)

    elif args.export_type == exports.constants.EXPORT_TYPE_CLICKSTREAM:
        export_request = ExportRequest.from_args(
            course_id=args.course_id,
            course_slug=args.course_slug,
            partner_id=args.partner_id,
            parter_short_name=args.partner_short_name,
            group_id=args.group_id,
            export_type=args.export_type,
            anonymity_level=args.anonymity_level,
            statement_of_purpose=args.statement_of_purpose,
            interval=args.interval,
            ignore_existing=args.ignore_existing)

    else:
        err_msg = 'Export type must be clickstream or tables, '
        'but found {}. Please visit https://github.com/coursera/'
        'courseraresearchexports for example usage.'.format(args.export_type)
        logging.error(err_msg)
        raise ValueError(err_msg)

    export_request_with_metadata = exports.api.post(export_request)[0]

    logging.info('Successfully created request {id}.'
                 .format(id=export_request_with_metadata.id))
    logging.debug('Request created with json body:\n{json}'
                  .format(json=json.dumps(
                        export_request_with_metadata.to_json(), indent=2)))


def get(args):
    """
    Get the details and status of a data export request using a job id.
    """
    export_request = exports.api.get(args.id)[0]

    export_request_info = [
        ['Export Job Id:', export_request.id],
        ['Export Type:', export_request.export_type],
        ['Status:', export_request.status],
        ['Scope Context:', export_request.scope_context],
        ['Scope Id:', export_request.scope_id],
        ['Created:', export_request.created_at.strftime('%c')]]

    if export_request.schema_names:
        export_request_info.append(
            ['Schemas:', export_request.schema_names])

    if export_request.download_link:
        export_request_info.append(
            ['Download Link:', export_request.download_link])

    if export_request.interval:
        export_request_info.append(
            ['Interval:', '_'.join(export_request.interval)])

    logging.info('\n' + tabulate(export_request_info, tablefmt="plain"))


def get_all(args):
    """
    Get the details and status of your data export requests.
    """
    export_requests = exports.api.get_all()

    export_requests_table = [['Created', 'Request Id', 'Status', 'Type',
                              'Scope', 'Schemas']]
    for export_request in sorted(export_requests, key=lambda x: x.created_at,
                                 reverse=True):
        export_requests_table.append([
            export_request.created_at.strftime('%Y-%m-%d'),
            export_request.id,
            export_request.status,
            export_request.export_type,
            export_request.scope_id,
            export_request.schema_names])

    logging.info('\n' + tabulate(export_requests_table, headers='firstrow'))


def download(args):
    """
    Download a data export job using a request id.
    """
    try:
        export_request = exports.api.get(args.id)[0]
        export_request.download(args.dest)

    except Exception as err:
        logging.error('Download failed.\n{err}'.format(err=err))
        raise


def get_clickstream_links(args):
    """
    Generate links for clickstream data exports
    """
    clickstream_links_request = ClickstreamDownloadLinksRequest.from_args(
        course_id=args.course_id,
        course_slug=args.course_slug,
        partner_id=args.partner_id,
        parter_short_name=args.partner_short_name,
        group_id=args.group_id,
        interval=args.interval)

    clickstream_download_links = exports.api.get_clickstream_download_links(
        clickstream_links_request)

    # TODO: add more descriptive information or option write to text file
    logging.info('\n' + tabulate(
        [[link] for link in clickstream_download_links],
        headers='firstrow'))


def parser(subparsers):
    parser_jobs = subparsers.add_parser(
        'jobs',
        help='Get status of current/completed research export job(s)',
        description='Command line tools for requesting and reviewing the '
        'status of Coursera research data exports. Please first authenticate '
        'with the OAuth2 client before making requests (courseraoauth2client '
        'config authorize --app manage-research-exports).',
        epilog='Please file bugs on github at: '
        'https://github.com/coursera/courseraresearchexports/issues. If you '
        'would like to contribute to this tool\'s development, check us out '
        'at: https://github.com/coursera/courseraresarchexports')

    jobs_subparsers = parser_jobs.add_subparsers()

    create_request_parser(jobs_subparsers)

    parser_get_all = jobs_subparsers.add_parser(
        'get_all',
        help=get_all.__doc__,
        description = get_all.__doc__)
    parser_get_all.set_defaults(func=get_all)

    parser_get = jobs_subparsers.add_parser(
        'get',
        help=get.__doc__,
        description=get.__doc__)
    parser_get.set_defaults(func=get)

    parser_get.add_argument(
        'id',
        help='Export job ID')

    parser_download = jobs_subparsers.add_parser(
        'download',
        help=download.__doc__,
        description=download.__doc__)
    parser_download.set_defaults(func=download)

    parser_download.add_argument(
        'id',
        help='Export request ID')

    parser_download.add_argument(
        '--dest',
        default='.',
        help='Destination folder')

    parser_clickstream_links = jobs_subparsers.add_parser(
        'clickstream_download_links',
        help='Get download links for completed eventing exports.')
    parser_clickstream_links.set_defaults(func=get_clickstream_links)

    create_scope_subparser(parser_clickstream_links)

    parser_clickstream_links.add_argument(
        '--interval',
        nargs=2,
        metavar=('START', 'END'),
        help='Interval of exported clickstream data, inclusive. '
        '(i.e. 2016-08-01 2016-08-04).')

    return parser_jobs


def create_scope_subparser(parser):
    scope_subparser = parser.add_mutually_exclusive_group(
        required=True)
    scope_subparser.add_argument(
        '--course_id',
        help='Export rows corresponding to learners within a course according '
        'to the unique id assigned by Coursera.')
    scope_subparser.add_argument(
        '--course_slug',
        help='Export rows corresponding to learners within a course according '
        'to the unique name of your course defined as the part after '
        '/learn in the course url. (e.g. machine-learning for '
        'https://www.coursera.org/learn/machine-learning).')
    scope_subparser.add_argument(
        '--partner_id',
        help='Export rows corresponding to learners within a partner.')
    scope_subparser.add_argument(
        '--partner_short_name',
        help='Export rows corresponding to learners within a partner.')
    scope_subparser.add_argument(
        '--group_id',
        help='Export rows corresponding to learners without a group.')


def create_request_parser(subparsers):
    parser_request = subparsers.add_parser(
        'request',
        help=request.__doc__,
        description=request.__doc__)
    parser_request.set_defaults(func=request)
    request_subparsers = parser_request.add_subparsers()

    # common arguments between schema and eventing exports
    request_args_parser = argparse.ArgumentParser(add_help=False)

    create_scope_subparser(request_args_parser)

    request_args_parser.add_argument(
        '--statement_of_purpose',
        required=True,
        help='Please let us know how you plan to use the '
        'data, what types of research questions you\'re asking, who will '
        'be working with the data primarily, and with whom you plan to '
        'share it.')

    # tables subcommand
    parser_tables = request_subparsers.add_parser(
        'tables',
        help='Create a data export request for specified tables.',
        description='Create a data export request for specified tables.',
        parents=[request_args_parser])

    parser_tables.add_argument(
        '--export_type',
        choices=exports.constants.EXPORT_TYPE_TABLES,
        default=exports.constants.EXPORT_TYPE_TABLES,
        help=argparse.SUPPRESS)

    parser_tables.add_argument(
        '--anonymity_level',
        choices=exports.constants.ANONYMITY_LEVELS,
        default=exports.constants.ANONYMITY_LEVEL_ISOLATED,
        help='{0} corresponds to data coordinator exports. '
        '{1} has different user id columns in every domain.'
        .format(exports.constants.ANONYMITY_LEVEL_COORDINATOR,
                exports.constants.ANONYMITY_LEVEL_ISOLATED))

    parser_tables.add_argument(
        '--schema_names',
        choices=exports.constants.SCHEMA_NAMES,
        nargs='+',
        default=exports.constants.SCHEMA_NAMES,
        help='Data schemas to export. Any combination of: ' +
             ', '.join(exports.constants.SCHEMA_NAMES))

    # clickstream subcommand
    parser_clickstream = request_subparsers.add_parser(
        'clickstream',
        help='Create a data export request for clickstream data. Only '
        'available for data coordinators.',
        description='Create a data export request for clickstream data. Only '
        'available for data coordinators.',
        parents=[request_args_parser])

    parser_clickstream.add_argument(
        '--export_type',
        choices=exports.constants.EXPORT_TYPE_CLICKSTREAM,
        default=exports.constants.EXPORT_TYPE_CLICKSTREAM,
        help=argparse.SUPPRESS)

    parser_clickstream.add_argument(
        '--anonymity_level',
        choices=exports.constants.ANONYMITY_LEVEL_COORDINATOR,
        default=exports.constants.ANONYMITY_LEVEL_COORDINATOR,
        help=argparse.SUPPRESS)

    parser_clickstream.add_argument(
        '--interval',
        nargs=2,
        metavar=('START', 'END'),
        help='Interval of clickstream data to be exported '
        '(i.e. 2016-08-01 2016-08-04). By default this will be the past day.')

    parser_clickstream.add_argument(
        '--ignore_existing',
        action='store_true',
        help='If flag is set, we will recompute clickstream data for all dates'
        'in the interval. Otherwise, previously computed days are skipped.')
