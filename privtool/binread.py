# This file is part of PrivTool, see <https://github.com/MestreLion/privtool>
# Copyright (C) 2021 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>

"""
    Functions for reading struct-ured data from binary files
"""

import logging
import struct


STC_INT    = struct.Struct('<I')
STC_OFFSET = struct.Struct('<H2s')

NUL = b'\0'


log = logging.getLogger(__name__)


class binopen:
    def __init__(self, path, mode='rb', **kwargs):
        # Padding used in offsets
        self.offset_pad = kwargs.pop('offset_pad', b'\x00\xE0')

        # Chunk size used when iterating on file
        self.chunk_size = kwargs.pop('chunk_size', 1)

        if 't' in mode:
            # Did you even notice the class name?
            log.warning("%s only supports binary modes, ignoring 't' in mode: %s",
                        self.__class__.__name__, mode)
            mode = mode.replace('t', '')
        if 'b' not in mode:
            mode += 'b'
        self._f = open(path, mode, **kwargs)

    @property
    def INT_SIZE(self):
        return STC_INT.size

    @property
    def OFFSET_SIZE(self):
        return STC_OFFSET.size

    def __enter__(self):
        return self

    def __exit__(self, *_a, **_kw):
        self._f.close()

    def __getattr__(self, item):
        # Proxying all method calls to file. This simple proxy only works because
        # __setattr__() is not defined, otherwise it would have to be more sophisticated.
        return getattr(self._f, item)

    def __iter__(self):
        return iter(lambda: self._f.read(self.chunk_size), b'')

    def read_int(self):
        return STC_INT.unpack(self._f.read(STC_INT.size))[0]

    def read_offset(self):
        off, pad = STC_OFFSET.unpack(self._f.read(STC_OFFSET.size))
        # Save the first padding
        if not self.offset_pad:
            self.offset_pad = pad
            log.debug("Offset padding: %s", self.offset_pad)
        # Check if padding matches
        elif not pad == self.offset_pad:
            log.warning("Padding mismatch in %s: %s, expected %s",
                        self._f.name, pad, self.offset_pad)
            self.offset_pad = pad
        return off

    def read_string(self, size, encoding='ascii'):
        s = struct.unpack(f'{size}s', self._f.read(size))[0]
        text, nul, junk = s.partition(NUL)
        if not nul or junk.strip(NUL):
            log.warning("Malformed NUL-terminated string, truncating: %s", s)
        return text[:size-1].decode(encoding)
