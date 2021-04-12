# This file is part of PrivTool, see <https://github.com/MestreLion/privtool>
# Copyright (C) 2021 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>

"""
    Command-line interface and supporting functions
"""
import argparse
import logging
import pprint

from . import __about__ as a
from . import model


log = logging.getLogger(__name__)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog=__package__,
        description=a.__description__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=a.epilog,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', '--quiet', dest='loglevel',
        const=logging.WARNING, default=logging.INFO, action="store_const",
        help="Suppress informative messages.")
    group.add_argument('-v', '-d', '--verbose', '--debug', dest='loglevel',
        const=logging.DEBUG, action="store_const",
        help="Verbose/Debug mode, output extra info.")

    parser.add_argument('path', metavar='SAVEFILE', help="Save file to read.")

    return parser.parse_args(argv)


def main(argv: list = None):
    logging.basicConfig(format='%(levelname)-8s: %(message)s')
    args = parse_args(argv)
    logging.getLogger().setLevel(args.loglevel)
    log.debug(args)

    pprint.pprint(model.Save(args.path).records)
