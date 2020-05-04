# -*- coding: utf-8 -*-
import struct

import array
import warnings
from pims.base_frames import Frame
import numpy as np

from nd2reader.exceptions import InvalidVersionError
from nd2reader.common import decode_str

class SyncParser(object):
    metadata = None

    """Parses ND2 files synchronously instead of relying on the stored
    metadata (which is wrong or incomplete in a lot of cases).

    """
    def __init__(self, fh):
        self._fh = fh

        self.parse()

    """Parse the whole file, store a representation of it but not the image
    data, to manage memory usage and keep accessing images efficient.  """
    def parse(self):
        # file version information
        print(self._collect_block_containing(b'ND2'))

        # ImageCalibration
        print(self._collect_block_containing(b'Image'))

    def _collect_block_containing(self, value_of_interest):
        value = decode_str(self._skip_to(value_of_interest))
        found = value_of_interest in value
        for block in self._read_block():
            if value_of_interest in block:
                found = True

            if found:
                value, search_on = self._collect_str(value, block)
                if not search_on:
                    break

        return value

    def _skip_to(self, to_value):
        for block in self._read_block():
            if to_value not in block:
                continue

            return b' '.join(block.split(b'\x00')).strip()

    def _collect_str(self, value, block):
        # Get the string from the current block of bytes
        converted = b' '.join(block.split(b'\x00')).strip()
        if len(converted) == 0:
            return value, False

        value += decode_str(converted)
        return value, True

    def _read_block(self):
        """Read through the file, 16 bytes at a time
        """
        block = True  # placeholder for the `while`
        while block:
            block = self._fh.read(16)
            if block:
                yield block
