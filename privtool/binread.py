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
STC_SIZE   = struct.Struct('>cH')

# Terminating byte for strings
NUL = b'\0'


log = logging.getLogger(__name__)


class binopen:
    """Extension of open() for binary files.

    Differences/Additions:
    - <mode> is always binary. Any 't' in <mode> will be ignored and log a warning.
    - Iterates on bytes instead of lines. Use iter_read() for a larger chunk size.
    - Returned object always have a 'name' property, set to DEFAULT_NAME if
        not available at the underlying, proxied file-like object (Streams).
    - <offset_pad> sets the default padding value expected by read_offset(), by
        default b'\x00\xE0'. This might be blank in future versions, which will
        set as default the padding found by the first read_offset() call.
    - read_*() methods for reading structured data, and their corresponding
        *_SIZE properties for bytes consumed by each method.
    - All other attributes, including methods, are proxied to the underlying
        file object.
    """
    DEFAULT_NAME = "file"

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

    @property
    def name(self):
        return getattr(self._f, 'name', self.DEFAULT_NAME)

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
        pos = self._f.tell()
        off, pad = STC_OFFSET.unpack(self._f.read(STC_OFFSET.size))
        if not padding:
            padding = self.offset_pad
        # Save the first padding found, for future calls
        if not padding:
            log.debug("Offset padding after position %s, now set as default for %s: %r",
                      pos, self.name, pad)
            self.offset_pad = pad
        # Check if padding matches
        elif not pad == padding:
            log.warning("Offset padding mismatch after position %s in %s:"
                        " expected %r, found %r. Setting it as the new default.",
                        pos, self.name, padding, pad)
            self.offset_pad = pad
        return off

    def read_fixed_string(self, size, encoding='ascii'):
        """Read <size> bytes from file and return the string up to the first NUL.

        The NUL terminator is expected to exist and not included in returned
        string, so maximum string length returned is <size>-1 even without a
        NUL on data. Missing the NUL, or any (discarded) non-NUL bytes after it,
        will log a warning.
        """
        pos = self._f.tell()
        s = struct.unpack(f'{size}s', self._f.read(size))[0]
        text, nul, junk = s.partition(NUL)
        if not nul or junk.strip(NUL):
            log.warning("Malformed NUL-terminated string after position %s in %s,"
                        " truncating it: %r", pos, self.name, s)
        return text[:size-1].decode(encoding)

    def read_string(self, max_size=None, encoding='ascii', return_size=False):
        """Read from file until NUL or up to <max_size>, and return the string.

        Returned string will not contain the terminating NUL. If <max_size> is
        None, read up to the end of file. The terminating NUL is not mandatory,
        so unlike read_fixed_string() this might return a string of <max_size>
        length, and will not log a warning if NUL was not found or end of file
        was reached.

        If <return_size>, return a 2-tuple (<string>, <size_read>). <size_read>
        does account for the terminating NUL if it was found.
        """
        pos = self._f.tell()
        buffer = b''
        i = 0
        while max_size is None or i < max_size:
            c = self._f.read(1)
            i += 1
            if c == NUL:
                break
            buffer += c
        assert i == self._f.tell() - pos
        text = buffer.decode(encoding)
        return (text, i) if return_size else text

    def read_record_header(self, max_size=None):
        """Return name, header size and data size of a record. API subject to change."""
        pos = self._f.tell()
        name, name_size = self.read_string(max_size=max_size, return_size=True)
        # Check to see if we had (or will have) a partial read:
        # - Name is blank or truncated (missed NIL)
        # - Max size is set and does not hold whole header
        if (not name or not len(name) == name_size-1 or
                (max_size is not None and max_size < name_size + STC_SIZE.size)):
            # Read whatever we can and return as binary data
            self._f.seek(pos)
            name = self._f.read() if max_size is None else self._f.read(max(0, max_size))
            size = len(name)
            return name, size, 0, True  # True for partial read
        pad, data_size = STC_SIZE.unpack(self._f.read(STC_SIZE.size))
        if not pad == NUL:
            log.warning("Padding mismatch after position %s in %s, record %r:"
                        " expected %r, found %r", pos, self.name, name, NUL, pad)
        return name, name_size + STC_SIZE.size, data_size, False

    def check_pos(self, expected_pos, who="it was", seek=True, warn=True):
        """Return True if file's current read position is <expected_pos>

        If it is not, then log a warning if <warn>, telling <who> was expecting it,
        and seek to this expected offset if <seek>.

        Used for testing read contiguity at on known offsets.
        """
        pos = self._f.tell()
        if pos == expected_pos:
            return True
        if warn:
            log.warning("%s is currently at read offset %s, %s expected %s",
                        self.name, pos, who, expected_pos)
        if seek:
            self._f.seek(expected_pos)
        return False
