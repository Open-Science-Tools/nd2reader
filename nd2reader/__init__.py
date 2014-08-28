import array
import numpy as np
import struct
import StringIO


class Nd2Reader(object):
    """
    Reads .nd2 files, provides an interface to the metadata, and generates numpy arrays from the image data.

    """
    def __init__(self, filename):
        self._filename = filename
        self._file_handler = None

    @property
    def file_handler(self):
        if self._file_handler is None:
            self._file_handler = open(self._filename, "rb")
        return self._file_handler

    @property
    def chunk_map_location(self):
        """
        The position in bytes from the beginning of the file where the chunk map begins.
        The chunk map is a series of string labels followed by the position (in bytes) of the respective data.

        """
        self.file_handler.seek(-8, 2)
        return struct.unpack("Q", self.file_handler.read(8))[0]

    def read_chunk(self, location):
        pass

    @staticmethod
    def as_numpy_array(arr):
        return np.frombuffer(arr)