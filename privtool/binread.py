# This file is part of PrivTool, see <https://github.com/MestreLion/privtool>
# Copyright (C) 2021 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>

"""
    Tools for reading struct-ured data from binary files
"""

import logging
import struct


# Pre-compiled support structures. Use binopen.*_SIZE for their sizes
STC_INT    = struct.Struct('<I')
STC_OFFSET = struct.Struct('<H2s')

# Terminating byte for strings
NUL = b'\0'


log = logging.getLogger(__name__)


class binopen:
    """Extension of open() for binary files.

    Differences/Additions:
    - <mode> is always binary. Any 't' in <mode> will be ignored and log a warning.
    - Iterates on files by byte instead of by line. Use iter_read() to choose a
        larger chunk size.
    - <offset_pad> sets the default padding value expected by read_offset(), by
        default b'\x00\xE0'. This might be blank in future versions, which will
        set as default the padding found by the first read_offset() call.
    - read_*() methods for reading structured data, and their corresponding
        *_SIZE properties for bytes consumed by each method.
    - All other attributes, including methods, are proxied to the underlying
        file object.
    """
    def __init__(self, path, mode='rb', **kwargs):
        # Default padding expected by read_offset()
        self.offset_pad = kwargs.pop('offset_pad', b'\x00\xE0')

        # Handle mode
        if 't' in mode:
            # Did you even notice the class name?
            log.warning("%s only supports binary modes, ignoring 't' in mode: %s",
                        self.__class__.__name__, mode)
            mode = mode.replace('t', '')
        if 'b' not in mode:
            mode += 'b'

        # Any exception raised in __init__() prevents __exit__() from triggering,
        # bypassing closing _f, so make sure this open() call comes last.
        self._f = open(path, mode, **kwargs)

    @property
    def INT_SIZE(self):
        # Convenience wrapper so callers don't have to deal with STC_INT directly,
        # with an added bonus of reflecting its real, current size if it changes.
        return STC_INT.size

    @property
    def OFFSET_SIZE(self):
        return STC_OFFSET.size

    def __enter__(self):
        # As for __init__(), any exception here prevents _f.close(), be extra careful!
        return self

    def __exit__(self, *_a, **_kw):
        self._f.close()

    def __getattr__(self, item):
        # Proxying all method calls to file. This simple proxy only works because
        # __setattr__() is not defined, otherwise it would have to be more sophisticated.
        return getattr(self._f, item)

    def __iter__(self):
        return self.iter_read(1)

    def iter_read(self, chunk_size=1):
        return iter(lambda: self._f.read(chunk_size), b'')

    def read_int(self):
        """Read and return a 4-byte little-endian integer from file"""
        return STC_INT.unpack(self._f.read(STC_INT.size))[0]

    def read_offset(self, padding=b''):
        """Read a 4-byte segment:offset from file and return the 2-byte offset.

        It is assumed the offset is the *first* 2 bytes, in little-endian notation.

        Segment is regarded as padding. It is compared to the expected <padding>,
        or to the default <offset_pad> set when file was opened, logging a warning
        whenever it changes and setting it as the new default for this file.

        Example, assuming the next 4 bytes on file are b'\x34\x12\xAA\xFF':
        file.read_offset() -> 0x1234 = 4660
        """
        off, pad = STC_OFFSET.unpack(self._f.read(STC_OFFSET.size))
        if not padding:
            padding = self.offset_pad
        # Save the first padding found, for future calls
        if not padding:
            log.debug("Offset padding, now set as default for this file: %r", pad)
            self.offset_pad = pad
        # Check if padding matches
        elif not pad == padding:
            log.warning("Padding mismatch in %s: %r, expected %r",
                        self._f.name, pad, padding)
            self.offset_pad = pad
        return off

    def read_string(self, size, encoding='ascii'):
        """Read <size> bytes from file and return the string up to the first NUL.

        The NUL terminator is expected to exist and not included in returned
        string, so maximum string length returned is <size>-1 even without a
        NUL on data. Missing the NUL, or any (discarded) non-NUL bytes after it,
        will log a warning.
        """
        s = struct.unpack(f'{size}s', self._f.read(size))[0]
        text, nul, junk = s.partition(NUL)
        if not nul or junk.strip(NUL):
            log.warning("Malformed NUL-terminated string, truncating: %r", s)
        return text[:size-1].decode(encoding)
