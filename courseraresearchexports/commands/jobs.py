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

from __future__ import print_function

import json
import logging

import argparse
from tabulate import tabulate

from courseraresearchexports.exports import api
from courseraresearchexports.constants.api_constants import \
    ANONYMITY_LEVEL_COORDINATOR, EXPORT_TYPE_CLICKSTREAM, \
    EXPORT_TYPE_TABLES, SCHEMA_NAMES
from courseraresearchexports.models.ClickstreamDownloadLinksRequest import \
    ClickstreamDownloadLinksRequest
from courseraresearchexports.models.ExportRequest import ExportRequest
from courseraresearchexports.exports import utils


def request_clickstream(args):
    """
    Create and send an clickstream data export request with Coursera. Only
    available for data coordinators.
    """
    export_request = ExportRequest.from_args(
        course_id=args.course_id,
        course_slug=args.course_slug,
        partner_id=args.partner_id,
        parter_short_name=args.partner_short_name,
        group_id=args.group_id,
        anonymity_level=ANONYMITY_LEVEL_COORDINATOR,
        statement_of_purpose=args.purpose,
        export_type=EXPORT_TYPE_CLICKSTREAM,
        interval=args.interval,
        ignore_existing=args.ignore_existing)

    export_request_with_metadata = api.post(export_request)[0]

    logging.info('Successfully created clickstream export request {id}.'
                 .format(id=export_request_with_metadata.id))
    logging.debug('Request created with json body:\n{json}'
                  .format(json=json.dumps(
                        export_request_with_metadata.to_json(), indent=2)))


def request_tables(args):
    """
    Create and send a tables data export request with Coursera.
    """
    export_request = ExportRequest.from_args(
        course_id=args.course_id,
        course_slug=args.course_slug,
        partner_id=args.partner_id,
        parter_short_name=args.partner_short_name,
        group_id=args.group_id,
        user_id_hashing=args.user_id_hashing,
        statement_of_purpose=args.purpose,
        export_type=EXPORT_TYPE_TABLES,
        schema_names=args.schemas)

    export_request_with_metadata = api.post(export_request)[0]

    logging.info('Successfully created tables export request {id}.'
                 .format(id=export_request_with_metadata.id))
    logging.debug('Request created with json body:\n{json}'
                  .format(json=json.dumps(
                        export_request_with_metadata.to_json(), indent=2)))


def get(args):
    """
    Get the details and status of a data export request using a job id.
    """
    export_request = api.get(args.id)[0]

    export_request_info = [
        ['Export Job Id:', export_request.id],
        ['Export Type:', export_request.export_type_display],
        ['Status:', export_request.status],
        ['Scope Context:', export_request.scope_context],
        ['Scope Id:', export_request.scope_id],
        ['Scope Name:', export_request.scope_name],
        ['User id Hashing: ', export_request.formatted_anonymity_level],
        ['Created:', export_request.created_at.strftime('%c')]]

    if export_request.schema_names:
        export_request_info.append(
            ['Schemas:', export_request.schema_names_display])

    if export_request.download_link:
        export_request_info.append(
            ['Download Link:', export_request.download_link])

    if export_request.interval:
        export_request_info.append(
            ['Interval:', ' to '.join(export_request.interval)])

    print(tabulate(export_request_info, tablefmt="plain"))


def get_all(args):
    """
    Get the details and status of your data export requests.
    """
    export_requests = api.get_all()

    export_requests_table = [['Created', 'Request Id', 'Status', 'Type',
                              'User Id Hashing', 'Scope', 'Schemas']]
    for export_request in sorted(export_requests, key=lambda x: x.created_at):
        export_requests_table.append([
            export_request.created_at.strftime('%Y-%m-%d %H:%M'),
            export_request.id,
            export_request.status,
            export_request.export_type_display,
            export_request.formatted_anonymity_level,
            export_request.scope_id,
            export_request.schema_names_display])

    print(tabulate(export_requests_table, headers='firstrow'))


def download(args):
    """
    Download a data export job using a request id.
    """
    try:
        export_request = api.get(args.id)[0]
        dest = args.dest
        utils.download(export_request, dest)
    except Exception as err:
        logging.error('Download failed with exception:\n{}'.format(err))
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

    clickstream_download_links = api.get_clickstream_download_links(
        clickstream_links_request)

    # TODO: add more descriptive information or option write to text file
    print(tabulate(
        [[link] for link in clickstream_download_links],
        tablefmt="plain"))


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
        description=get_all.__doc__)
    parser_get_all.set_defaults(func=get_all)

    parser_get = jobs_subparsers.add_parser(
        'get',
        help=get.__doc__,
        description=get.__doc__)
    parser_get.set_defaults(func=get)

    parser_get.add_argument(
        'id',
        help='Export request ID')

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
        help='Create and send a data export request with Coursera.',
        description='Create and send a data export request with Coursera. '
        'Use subcommands to specify the export request type.')
    request_subparsers = parser_request.add_subparsers()

    # common arguments between schema and eventing exports
    request_args_parser = argparse.ArgumentParser(add_help=False)

    create_scope_subparser(request_args_parser)

    request_args_parser.add_argument(
        '--purpose',
        required=True,
        help='Please let us know how you plan to use the '
        'data, what types of research questions you\'re asking, who will '
        'be working with the data primarily, and with whom you plan to '
        'share it.')

    # tables subcommand
    parser_tables = request_subparsers.add_parser(
        'tables',
        help=request_tables.__doc__,
        description=request_tables.__doc__,
        parents=[request_args_parser])
    parser_tables.set_defaults(func=request_tables)

    parser_tables.add_argument(
        '--user_id_hashing',
        choices=['linked', 'isolated'],
        default='isolated',
        help='The level of user_id hashing in the data export. With \'linked\''
        ' user_id hashing, users can be identified between table schemas. '
        'With \'isolated\' user_id hashing, users have independent ids in'
        'different schemas and cannot be linked. Only data coordinators have '
        'access to \'linked\' users_ids to restrict PII.')

    parser_tables.add_argument(
        '--schemas',
        choices=SCHEMA_NAMES,
        nargs='+',
        default=SCHEMA_NAMES,
        help='Data schemas to export. Any combination of: {}. By default this '
        'will be all available schemas.'.format(
            ', '.join(SCHEMA_NAMES)))

    # clickstream subcommand
    parser_clickstream = request_subparsers.add_parser(
        'clickstream',
        help=request_clickstream.__doc__,
        description=request_clickstream.__doc__,
        parents=[request_args_parser])
    parser_clickstream.set_defaults(func=request_clickstream)

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
