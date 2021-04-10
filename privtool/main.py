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

    offsets = []
    mission_headers = []
    with b.binopen(path) as f:
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
            offsets.append(f.read_offset())
            log.debug("Unknown offset: %s", offsets[-1])

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

        off_current = f.tell()
        f.seek(off_playername)
        playername = f.read_string(MAX_SIZE_PLAYERNAME)
        callsign   = f.read_string(MAX_SIZE_CALLSIGN)
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
