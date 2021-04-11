# PrivTool - Library and editor for 'Wing Commander: Privateer' saved games
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

import logging
import os.path

import argparse

from . import __copyright__, __email__
from . import binread as b


log = logging.getLogger(__name__)


class Save:
    def __init__(self, path: str = ""):
        self.path = ""
        self.missions = []
        self.forms = []
        self.records = []
        if path:
            self.load(path)

    def load(self, path):
        self.path = path
        return load(path)


HEAD_OFFSETS = 6
MISSION_HEAD_SIZE  = 8

MAX_SIZE_PLAYERNAME = 18  # Weird, but true. Includes '\0' NUL terminator
MAX_SIZE_CALLSIGN = 15
MAX_NUM_MISSIONS = 4

RECORD_CONTAINERS = ('FORM', 'REALFORM', 'FFORM')


def load(path):
    """For now, a monolithic top-level function"""
    # TOP: 16 + 8 * num_missions
    #   file_size
    #   offset PLAYER_PARMS
    #   offset GAMEPLAY_PARMS
    #   offset DATA_PARMS
    #   missions_head: num_missions * data[8]
    # HEAD: 24
    #   offset FORM_0
    #   offset special
    #   offset FORM_1
    #   offset FORM_2
    #   offset PLAYERNAME
    #   offset CALLSIGN
    # PLAYER_PARMS: 9
    # GAMEPLAY_PARMS: variable
    # DATA_PARMS: variable
    # RECORDS:
    #   string 'NAME'\0
    #   pad[1] = \0
    #   data_size[2] (BIG Endian!)
    #   data[data_size]
    # if record NAME is FORM, REALFORM, FFORM: record is a container (Form)

    offsets = []
    record_offsets = []
    mission_headers = []
    with b.binopen(path) as f:
        # TOP #################################################################
        file_size    = f.read_int()
        off_player   = f.read_offset()
        off_gameplay = f.read_offset()
        off_data     = f.read_offset()
        off_head     = off_player - HEAD_OFFSETS * f.OFFSET_SIZE

        log.debug(", ".join((
            "file_size = %(file_size)s",
            "off_head = %(off_head)s",
            "off_player = %(off_player)s",
            "off_gameplay = %(off_gameplay)s",
            "off_data = %(off_data)s",
        )), locals())

        if file_size != os.path.getsize(path):
            log.warning("File size mismatch in %s: %s, expected %s",
                        path, os.path.getsize(path), file_size)

        # Mission headers
        num_missions = (off_head - f.tell()) / MISSION_HEAD_SIZE
        if not num_missions == int(num_missions):
            log.error("Number of missions is not an integer: %s"
                      " [offset=%s, off_head=%s, off_player=%s]",
                      num_missions, f.tell(), off_head, off_player)
            return
        num_missions = int(num_missions)
        log.info("num_missions = %s", num_missions)
        if not 0 <= num_missions <= MAX_NUM_MISSIONS:
            log.warning("Non-standard number of missions: %s, expected at most %s",
                        num_missions, MAX_NUM_MISSIONS)
        for i in range(num_missions):
            mission_headers.append(f.read(MISSION_HEAD_SIZE))
            log.debug("Mission %s header: %s", i, mission_headers[-1])

        # HEAD ################################################################
        # The 2nd offset is to unknown data, the last 2 are name and callsign
        for i in range(HEAD_OFFSETS - 2):
            if i == 1:
                log.debug("Unknown data offset %4d", f.read_offset())
                continue
            record_offsets.append(f.read_offset())
            log.debug("FORM at file offset %4d", record_offsets[-1])

        off_playername = f.read_offset()
        off_callsign   = f.read_offset()
        log.debug(", ".join((
            "off_playername = %(off_playername)s",
            "off_callsign = %(off_callsign)s",
        )), locals())
        if (
            (not off_playername + MAX_SIZE_PLAYERNAME == off_callsign) or
            (not off_callsign   + MAX_SIZE_CALLSIGN   == file_size)
        ):
            log.warning("Name/Callsign offset mismatch for file size %s: %s, %s",
                        file_size, off_playername, off_callsign)

        # *_PARMS #############################################################
        # As we're not reading them yet, position file cursor as if we did
        f.seek(record_offsets[0])

        # Records #############################################################
        forms = 0
        for offset in record_offsets:
            _size, forms = read_record(f, offset, forms=forms)

        # Name and Callsign ###################################################
        f.check_pos(off_playername, "sort of")  # yeah, it overlaps 1 byte
        playername = f.read_fixed_string(MAX_SIZE_PLAYERNAME)
        callsign   = f.read_fixed_string(MAX_SIZE_CALLSIGN)
        log.info("%r / %r ", playername, callsign)
        f.check_pos(file_size)


def read_record(f, offset, max_size=None, forms=0, level=0):
    f.check_pos(offset)
    name, hsize, dsize, partial = f.read_record_header(max_size)
    size = hsize + dsize
    indent = ' ' * 4 * level

    if partial:
        # Will soon be downgraded to DEBUG, as this seems to be expected
        log.warning("Partial record data after offset %s, size %d: %r",
                    offset, size, name)
        return size, forms

    if max_size is not None and max_size < dsize:
        log.warning("Declared %s bytes of data would exceed parent's %s"
                    " remaining size. Adjusting data size to fit.",
                    dsize, max_size)
        adj = f" (originally {dsize:3d})"
        dsize = max_size
    else:
        adj = ""

    if level == 0 and not name == 'FORM':
        log.warning("Top-level record is expected to be a FORM")

    # Leaf record
    if name not in RECORD_CONTAINERS:
        log.info("%s%-8s offset %3d, total size %3d: header %2d, data %3d%s",
                 indent, name, offset, size, hsize, dsize, adj)
        data = f.read(dsize)
        log.debug(data)
        return size, forms

    # Containers (*FORM)
    fullname = f'{name}-{forms:02d}'
    bar = '-' * (5 + max(0, 15 * (3 - level)))
    log.info("%sBEGIN %s offset %3d, total size %3d: header %2d, data %3d%s %s",
             indent, fullname, offset, size, hsize, dsize, adj, bar)
    rsize = 0
    forms += 1
    while rsize < dsize:
        sz, forms = read_record(f, offset + hsize + rsize, dsize-rsize, forms, level+1)
        rsize += sz
    log.info("%sEND   %s, %s data bytes read %s%s",
             indent, fullname, rsize, bar, 28*'-')
    if not rsize == dsize:
        log.warning("Data size mismatch for %s: declared %s, actual record data is %s",
                    fullname, dsize, rsize)
        size = hsize + rsize
    return size, forms


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog=__package__,
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join((f"{__copyright__} <{__email__}>",
                          "License: GPLv3 or later, at your choice. "
                          "See <http://www.gnu.org/licenses/gpl>")),
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

    Save(args.path)
