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

"""
Wrapper around Coursera OAuth2 client.
"""

from courseraoauth2client.commands import config as oauth2config
from courseraresearchexports.exports.api import RESEARCH_EXPORTS_APP
import argparse


def parser(subparsers):
    # create the parser for the configure subcommand. (authentication / etc.)
    parser_config = subparsers.add_parser(
        'config',
        help='Configure %(prog)s for operation!')
    app_subparser = argparse.ArgumentParser(add_help=False)
    app_subparser.set_defaults(app=RESEARCH_EXPORTS_APP)

    app_subparser.add_argument(
        '--reconfigure',
        action='store_true',
        help='Reconfigure existing app?')

    config_subparsers = parser_config.add_subparsers()

    parser_authorize = config_subparsers.add_parser(
        'authorize',
        help=oauth2config.authorize.__doc__,
        parents=[app_subparser])
    parser_authorize.set_defaults(func=oauth2config.authorize)

    # Ensure your auth is set up correctly
    parser_check_auth = config_subparsers.add_parser(
        'check-auth',
        help=oauth2config.check_auth.__doc__,
        parents=[app_subparser])
    parser_check_auth.set_defaults(func=oauth2config.check_auth)

    parser_local_cache = config_subparsers.add_parser(
        'display-auth-cache',
        help=oauth2config.display_auth_cache.__doc__,
        parents=[app_subparser])
    parser_local_cache.set_defaults(func=oauth2config.display_auth_cache)
    parser_local_cache.add_argument(
        '--no-truncate',
        action='store_true',
        help='Do not truncate the keys [DANGER!!]')

    return parser_config
