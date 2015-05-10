# -*- coding: utf-8 -*-

from abc import abstractproperty
import array
from collections import namedtuple
import numpy as np
import struct
import re
from StringIO import StringIO
from nd2reader.model import Image

field_of_view = namedtuple('FOV', ['number', 'x', 'y', 'z', 'pfs_offset'])


class Nd2FileReader(object):
    CHUNK_HEADER = 0xabeceda
    CHUNK_MAP_START = "ND2 FILEMAP SIGNATURE NAME 0001!"
    CHUNK_MAP_END = "ND2 CHUNK MAP SIGNATURE 0000001!"
    
    """
    Reads .nd2 files, provides an interface to the metadata, and generates numpy arrays from the image data.

    """
    def __init__(self, filename):
        self._absolute_start = None
        self._filename = filename
        self._file_handler = None
        self._channel_offset = None
        self._chunk_map_start_location = None
        self._cursor_position = None
        self._label_map = {}
        self._metadata = {}
        self._read_map()
        self._parse_metadata()
        self.__dimensions = None

    @staticmethod
    def as_numpy_array(arr):
        return np.frombuffer(arr)

    def get_image(self, time_index, fov, channel_name, z_level):
        image_set_number = self._calculate_image_set_number(time_index, fov, z_level)
        timestamp, raw_image_data = self.get_raw_image_data(image_set_number, self.channel_offset[channel_name])
        return Image(timestamp, raw_image_data, fov, channel_name, z_level, self.height, self.width)

    @abstractproperty
    def channels(self):
        raise NotImplemented

    @property
    def height(self):
        """
        :return:    height of each image, in pixels

        """
        return self._metadata['ImageAttributes']['SLxImageAttributes']['uiHeight']

    @property
    def width(self):
        """
        :return:    width of each image, in pixels

        """
        return self._metadata['ImageAttributes']['SLxImageAttributes']['uiWidth']

    @property
    def _dimensions(self):
        if self.__dimensions is None:
            # The particular slot that this data shows up in changes (seemingly) randomly
            for line in self._metadata['ImageTextInfo']['SLxImageTextInfo'].values():
                if "Dimensions:" in line:
                    metadata = line
                    break
            else:
                raise Exception("Could not parse metadata dimensions!")
            for line in metadata.split("\r\n"):
                if line.startswith("Dimensions:"):
                    self.__dimensions = line
                    break
        return self.__dimensions


    @property
    def fh(self):
        if self._file_handler is None:
            self._file_handler = open(self._filename, "rb")
        return self._file_handler

    @property
    def time_index_count(self):
        """
        The number of image sets. If images were acquired using some kind of cycle, all images at each step in the
        program will have the same timestamp (even though they may have varied by a few seconds in reality). For example,
        if you have four fields of view that you're constantly monitoring, and you take a bright field and GFP image of
        each, and you repeat that process 100 times, you'll have 800 individual images. But there will only be 400
        time indexes.

        :rtype:     int

        """
        pattern = r""".*?T'\((\d+)\).*?"""
        try:
            count = int(re.match(pattern, self._dimensions).group(1))
        except AttributeError:
            return 1
        else:
            return count

    @property
    def z_level_count(self):
        pattern = r""".*?Z\((\d+)\).*?"""
        try:
            count = int(re.match(pattern, self._dimensions).group(1))
        except AttributeError:
            return 1
        else:
            return count

    @property
    def field_of_view_count(self):
        """
        The metadata contains information about fields of view, but it contains it even if some fields
        of view were cropped. We can't find anything that states which fields of view are actually
        in the image data, so we have to calculate it. There probably is something somewhere, since
        NIS Elements can figure it out, but we haven't found it yet.

        """
        pattern = r""".*?XY\((\d+)\).*?"""
        try:
            count = int(re.match(pattern, self._dimensions).group(1))
        except AttributeError:
            return 1
        else:
            return count

    @property
    def channel_count(self):
        pattern = r""".*?λ\((\d+)\).*?"""
        try:
            count = int(re.match(pattern, self._dimensions).group(1))
        except AttributeError:
            return 1
        else:
            return count

    @property
    def _image_count(self):
        return self._metadata['ImageAttributes']['SLxImageAttributes']['uiSequenceCount']

    @property
    def _sequence_count(self):
        return self._metadata['ImageEvents']['RLxExperimentRecord']['uiCount']

    @property
    def channel_offset(self):
        """
        Image data is interleaved for each image set. That is, if there are four images in a set, the first image
        will consist of pixels 1, 5, 9, etc, the second will be pixels 2, 6, 10, and so forth. Why this would be the
        case is beyond me, but that's how it works.

        """
        if self._channel_offset is None:
            self._channel_offset = {}
            for n, channel in enumerate(self.channels):
                self._channel_offset[channel.name] = n
        return self._channel_offset

    def _calculate_image_set_number(self, time_index, fov, z_level):
        return time_index * self.field_of_view_count * self.z_level_count + (fov * self.z_level_count + z_level)

    def get_raw_image_data(self, image_set_number, channel_offset):
        chunk = self._label_map["ImageDataSeq|%d!" % image_set_number]
        data = self._read_chunk(chunk)
        timestamp = struct.unpack("d", data[:8])[0]
        # The images for the various channels are interleaved within each other.
        image_data = array.array("H", data)
        image_data_start = 4 + channel_offset
        return timestamp, image_data[image_data_start::self.channel_count]

    def _parse_metadata(self):
        for label in self._label_map.keys():
            if not label.endswith("LV!") or "LV|" in label:
                continue
            data = self._read_chunk(self._label_map[label])
            stop = label.index("LV")
            self._metadata[label[:stop]] = self._read_file(data, 1)

    def _read_map(self):
        """
        Every label ends with an exclamation point, however, we can't directly search for those to find all the labels
        as some of the bytes contain the value 33, which is the ASCII code for "!". So we iteratively find each label,
        grab the subsequent data (always 16 bytes long), advance to the next label and repeat.

        """
        self.fh.seek(-8, 2)
        chunk_map_start_location = struct.unpack("Q", self.fh.read(8))[0]
        self.fh.seek(chunk_map_start_location)
        raw_text = self.fh.read(-1)
        label_start = raw_text.index(Nd2FileReader.CHUNK_MAP_START) + 32

        while True:
            data_start = raw_text.index("!", label_start) + 1
            key = raw_text[label_start: data_start]
            location, length = struct.unpack("QQ", raw_text[data_start: data_start + 16])
            if key == Nd2FileReader.CHUNK_MAP_END:
                # We've reached the end of the chunk map
                break
            self._label_map[key] = location
            label_start = data_start + 16

    def _read_chunk(self, chunk_location):
        """
        Gets the data for a given chunk pointer

        """
        self.fh.seek(chunk_location)
        # The chunk metadata is always 16 bytes long
        chunk_metadata = self.fh.read(16)
        header, relative_offset, data_length = struct.unpack("IIQ", chunk_metadata)
        if header != Nd2FileReader.CHUNK_HEADER:
            raise ValueError("The ND2 file seems to be corrupted.")
        # We start at the location of the chunk metadata, skip over the metadata, and then proceed to the
        # start of the actual data field, which is at some arbitrary place after the metadata.
        self.fh.seek(chunk_location + 16 + relative_offset)
        return self.fh.read(data_length)

    def _z_level_count(self):
        name = "CustomData|Z!"
        st = self._read_chunk(self._label_map[name])
        return len(array.array("d", st))

    def _parse_unsigned_char(self, data):
        return struct.unpack("B", data.read(1))[0]

    def _parse_unsigned_int(self, data):
        return struct.unpack("I", data.read(4))[0]

    def _parse_unsigned_long(self, data):
        return struct.unpack("Q", data.read(8))[0]

    def _parse_double(self, data):
        return struct.unpack("d", data.read(8))[0]

    def _parse_string(self, data):
        value = data.read(2)
        while not value.endswith("\x00\x00"):
            # the string ends at the first instance of \x00\x00
            value += data.read(2)
        return value.decode("utf16")[:-1].encode("utf8")

    def _parse_char_array(self, data):
        array_length = struct.unpack("Q", data.read(8))[0]
        return array.array("B", data.read(array_length))

    def _parse_metadata_item(self, args):
        data, cursor_position = args
        new_count, length = struct.unpack("<IQ", data.read(12))
        length -= data.tell() - cursor_position
        next_data_length = data.read(length)
        value = self._read_file(next_data_length, new_count)
        # Skip some offsets
        data.read(new_count * 8)
        return value

    def _get_value(self, data, data_type):
        parser = {1: {'method': self._parse_unsigned_char, 'args': data},
                  2: {'method': self._parse_unsigned_int, 'args': data},
                  3: {'method': self._parse_unsigned_int, 'args': data},
                  5: {'method': self._parse_unsigned_long, 'args': data},
                  6: {'method': self._parse_double, 'args': data},
                  8: {'method': self._parse_string, 'args': data},
                  9: {'method': self._parse_char_array, 'args': data},
                  11: {'method': self._parse_metadata_item, 'args': (data, self._cursor_position)}}
        return parser[data_type]['method'](parser[data_type]['args'])

    def _read_file(self, data, count):
        data = StringIO(data)
        metadata = {}
        for _ in xrange(count):
            self._cursor_position = data.tell()
            header = data.read(2)
            if not header:
                break
            data_type, name_length = map(ord, header)
            name = data.read(name_length * 2).decode("utf16")[:-1].encode("utf8")
            value = self._get_value(data, data_type)
            if name not in metadata:
                metadata[name] = value
            else:
                if not isinstance(metadata[name], list):
                    # We have encountered this key exactly once before. Since we're seeing it again, we know we
                    # need to convert it to a list before proceeding.
                    metadata[name] = [metadata[name]]
                # We've encountered this key before so we're guaranteed to be dealing with a list. Thus we append
                # the value to the already-existing list.
                metadata[name].append(value)
        return metadata