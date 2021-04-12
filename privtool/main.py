# PrivTool - Library and editor for 'Wing Commander: Privateer' save files
#
#    Copyright (C) 2021 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. See <http://www.gnu.org/licenses/gpl.html>

"""
    Privateer Save Game Library / Editor

Inspired by and made possible thanks to PREDIT from Wayne Sikes
"""
import argparse
import json
import logging

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

    print(json.dumps(model.Save(args.path).records))
