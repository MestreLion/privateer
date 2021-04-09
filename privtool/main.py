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
import struct
import sys


OFFSET_PAD = b''  # Padding used in offsets. Most likely always b'\x00\xE0'

log = logging.getLogger('privateer')


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


def load(path):
    """For now, a monolithic top-level function"""
    # TOP: 16 + 8 * num_missions
    #   file_size
    #   offset PLAYER_PARMS
    #   offset GAMEPLAY_PARMS
    #   offset DATA_PARMS
    #   mission_data: num_missions * data[8]
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
    STC_INT    = struct.Struct('<I')
    STC_OFFSET = struct.Struct('<H2s')
    HEAD_SIZE = 6 * STC_INT.size
    MISSION_HEAD_SIZE  = 8
    MAX_SIZE_PLAYERNAME = 18  # Weird, but true. Includes '\0' NUL terminator
    MAX_SIZE_CALLSIGN = 15
    MAX_NUM_MISSIONS = 4
    NUL = b'\0'

    def read_value(stc: struct.Struct):
        return stc.unpack(f.read(stc.size))[0]

    def read_int():
        return STC_INT.unpack(f.read(STC_INT.size))[0]

    def read_offset():
        global OFFSET_PAD
        off, pad = STC_OFFSET.unpack(f.read(STC_OFFSET.size))
        # Save the first padding
        if not OFFSET_PAD:
            OFFSET_PAD = pad
            log.debug("Offset padding: %s", OFFSET_PAD)
        # Check if padding matches
        elif not pad == OFFSET_PAD:
            log.warning("Padding mismatch in %s: %s, expected %s",
                        f.name, pad, OFFSET_PAD)
            OFFSET_PAD = pad
        return off

    def read_string(sz):
        s = struct.unpack(f'{sz}s', f.read(sz))[0]
        text, nul, junk = s.partition(NUL)
        if not nul or junk.strip(NUL):
            log.warning("Malformed NUL-terminated string, truncating: %s", s)
        return text[:sz-1].decode('ascii')

    offsets = []
    mission_headers = []
    with open(path, 'rb') as f:
        file_size    = read_int()
        off_player   = read_offset()
        off_gameplay = read_offset()
        off_data     = read_offset()
        off_head     = off_player - HEAD_SIZE
        log.debug(", ".join((
            "file_size = %(file_size)s",
            "off_head = %(off_head)s",
            "off_player = %(off_player)s",
            "off_gameplay = %(off_gameplay)s",
            "off_data = %(off_data)s",
        )), locals())

        num_missions = (off_head - f.tell()) / MISSION_HEAD_SIZE
        if not num_missions == int(num_missions):
            log.error("Number of missions is not an integer: %s"
                      " [offset=%s, off_head=%s, off_player=%s]",
                      num_missions, f.tell(), off_head, off_player)
            return
        num_missions = int(num_missions)
        log.info("num_missions = %s", num_missions)

        for i in range(num_missions):
            mission_headers.append(f.read(MISSION_HEAD_SIZE))
            log.debug("Mission %s header: %s", i, mission_headers[-1])

        for i in range(4):
            offsets.append(read_offset())
            log.debug("Unknown offset: %s", offsets[-1])

        off_playername = read_offset()
        off_callsign   = read_offset()
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

        off_current = f.tell()
        f.seek(off_playername)
        playername = read_string(MAX_SIZE_PLAYERNAME)
        callsign   = read_string(MAX_SIZE_CALLSIGN)
        log.info("%r / %r ", playername, callsign)
        f.seek(off_current)

    if not 0 <= num_missions <= MAX_NUM_MISSIONS:
        log.warning("Non-standard number of missions: %s", num_missions)

    if file_size != os.path.getsize(path):
        log.warning("File size mismatch in %s: %s, expected %s",
                    path, os.path.getsize(path), file_size)


def main(argv: list = None):
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)-5.5s: %(message)s')
    usage = "Usage: privtool SAVEFILE"
    if not argv or len(argv) < 2:
        log.error("Missing required argument SAVEFILE")
        log.error(usage)
        return 1

    Save(argv[1])
