import array
import numpy as np
import re
import struct
from pprint import pprint


class Nd2Reader(object):
    """
    Reads .nd2 files, provides an interface to the metadata, and generates numpy arrays from the image data.

    """
    def __init__(self, filename):
        self._filename = filename
        self._file_handler = None
        self._chunk_map_start_location = None
        self._map_keys = {}
        self._read_map()

    @property
    def fh(self):
        if self._file_handler is None:
            self._file_handler = open(self._filename, "rb")
        return self._file_handler

    def _read_map(self):
        """
        Every label ends with an exclamation point, however, we can't directly search for those to find all the labels
        as some of the bytes contain the value 33, which is the ASCII code for "!". So we iteratively find each label,
        grab the subsequent data (always 16 bytes long), advance to the next label and repeat.

        """
        raw_text = self.raw_chunk_map_text
        label_start = self._find_first_label_offset(raw_text)
        while True:
            data_start = self._get_data_start(label_start, raw_text)
            label, value = self._extract_map_key(label_start, data_start, raw_text)
            if label == "ND2 CHUNK MAP SIGNATURE 0000001!":
                # We've reached the end of the chunk map
                break
            self._map_keys[label] = value
            label_start = data_start + 16

    @staticmethod
    def _find_first_label_offset(raw_text):
        """
        The chunk map starts with some number of (seemingly) useless bytes, followed
        by "ND2 FILEMAP SIGNATURE NAME 0001!". We return the location of the first character after this sequence,
        which is the actual beginning of the chunk map.

        """
        return raw_text.index("ND2 FILEMAP SIGNATURE NAME 0001!") + 32

    @staticmethod
    def _get_data_start(label_start, raw_text):
        """
        The data for a given label begins immediately after the first exclamation point

        """
        return raw_text.index("!", label_start) + 1

    @staticmethod
    def _extract_map_key(label_start, data_start, raw_text):
        """
        Chunk map entries are a string label of arbitrary length followed by 16 bytes of data, which represent
        the byte offset from the beginning of the file where that data can be found.

        """
        key = raw_text[label_start: data_start]
        value = struct.unpack("QQ", raw_text[data_start: data_start + 16])
        return key, value

    @property
    def chunk_map_start_location(self):
        """
        The position in bytes from the beginning of the file where the chunk map begins.
        The chunk map is a series of string labels followed by the position (in bytes) of the respective data.

        """
        if self._chunk_map_start_location is None:
            # Put the cursor 8 bytes before the end of the file
            self.fh.seek(-8, 2)
            # Read the last 8 bytes of the file
            self._chunk_map_start_location = struct.unpack("Q", self.fh.read(8))[0]
        return self._chunk_map_start_location

    @property
    def raw_chunk_map_text(self):
        """
        Reads the entire chunk map and returns it as a string.

        """
        self.fh.seek(self.chunk_map_start_location)
        return self.fh.read(-1)

    @staticmethod
    def as_numpy_array(arr):
        return np.frombuffer(arr)