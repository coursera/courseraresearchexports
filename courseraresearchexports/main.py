#!/usr/bin/env python

# PYTHON_ARGCOMPLETE_OK

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
Coursera's tools for interacting with research data exports.

You may install it from source, or via pip.
"""

import argcomplete
import argparse
import logging
import sys

from courseraresearchexports import commands
from courseraresearchexports.commands import utils


def build_parser():
    """
    Build an argparse argument parser to parse the command line.
    """

    parser = argparse.ArgumentParser(
        description="""Coursera tools for interacting with research exports.
        There are a number of subcommands, each with their own help
        documentation. Feel free to view them by executing `%(prog)s
        SUB_COMMAND -h`. For example: `%(prog)s jobs -h`.""",
        epilog="""Please file bugs on github at:
        https://github.com/coursera/courseraresearchexports/issues. If you
        would like to contribute to this tool's development, check us out at:
        https://github.com/coursera/courseraresarchexports""")

    utils.add_logging_parser(parser)

    # We have a number of subcommands. These subcommands have their own
    # subparsers. Each subcommand should set a default value for the 'func'
    # option. We then call the parsed 'func' function, and execution carries on
    # from there.
    subparsers = parser.add_subparsers()

    # create the parser for the version subcommand.
    commands.version.parser(subparsers)

    # create the parser for the jobs subcommand.
    commands.jobs.parser(subparsers)

    # create the parser for the containers subcommand.
    commands.containers.parser(subparsers)

    # create the parser for the db subcommand.
    commands.db.parser(subparsers)

    return parser


def main():
    """
    Boots up the command line tool
    """
    logging.captureWarnings(True)
    parser = build_parser()

    argcomplete.autocomplete(parser)

    args = parser.parse_args()
    # Configure logging
    args.setup_logging(args)
    # Dispatch into the appropriate subcommand function.
    try:
        return args.func(args)
    except SystemExit:
        raise
    except:
        logging.exception('Problem when running command. Sorry!')
        sys.exit(1)


if __name__ == "__main__":
    main()
