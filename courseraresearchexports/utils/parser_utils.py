import logging
import sys

import requests


def add_logging_parser(main_parser):
    """Build an argparse argument parser to parse the command line."""

    main_parser.set_defaults(setup_logging=set_logging_level)

    verbosity_group = main_parser.add_mutually_exclusive_group(required=False)
    verbosity_group.add_argument(
        '--verbose',
        '-v',
        action='count',
        help='Output more verbose logging. Can be specified multiple times.')
    verbosity_group.add_argument(
        '--quiet',
        '-q',
        action='count',
        help='Output less information to the console during operation. Can be '
        'specified multiple times.')

    main_parser.add_argument(
        '--silence-urllib3',
        action='store_true',
        help='Silence urllib3 warnings. See '
        'https://urllib3.readthedocs.org/en/latest/security.html for details.')

    return verbosity_group


def set_logging_level(args):
    """Computes and sets the logging level from the parsed arguments."""
    root_logger = logging.getLogger()
    level = logging.INFO
    logging.getLogger('requests.packages.urllib3').setLevel(logging.WARNING)
    if "verbose" in args and args.verbose is not None:
        logging.getLogger('requests.packages.urllib3').setLevel(0)  # Unset
        if args.verbose > 1:
            level = 5  # "Trace" level
        elif args.verbose > 0:
            level = logging.DEBUG
        else:
            logging.critical("verbose is an unexpected value. {} exiting."
                             .format(args.verbose))
            sys.exit(2)
    elif "quiet" in args and args.quiet is not None:
        if args.quiet > 1:
            level = logging.ERROR
        elif args.quiet > 0:
            level = logging.WARNING
        else:
            logging.critical("quiet is an unexpected value. {} exiting."
                             .format(args.quiet))
    if level is not None:
        root_logger.setLevel(level)

    if args.silence_urllib3:
        # See: https://urllib3.readthedocs.org/en/latest/security.html
        requests.packages.urllib3.disable_warnings()