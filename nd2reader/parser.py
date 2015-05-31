# -*- coding: utf-8 -*-

import array
from datetime import datetime
import numpy as np
import re
import struct
import six


class Nd2Parser(object):
    """
    Reads .nd2 files, provides an interface to the metadata, and generates numpy arrays from the image data.
    You should not ever need to instantiate this class manually unless you're a developer.

    """
    CHUNK_HEADER = 0xabeceda
    CHUNK_MAP_START = six.b("ND2 FILEMAP SIGNATURE NAME 0001!")
    CHUNK_MAP_END = six.b("ND2 CHUNK MAP SIGNATURE 0000001!")

    def __init__(self, filename):
        self._filename = filename
        self._fh = None
        self._chunk_map_start_location = None
        self._cursor_position = 0
        self._dimension_text = None
        self._label_map = {}
        self.metadata = {}
        self._read_map()
        self._parse_metadata()

    @property
    def _file_handle(self):
        if self._fh is None:
            self._fh = open(self._filename, "rb")
        return self._fh

    def _get_raw_image_data(self, image_group_number, channel_offset):
        """
        Reads the raw bytes and the timestamp of an image.

        :param image_group_number: groups are made of images with the same time index, field of view and z-level.
        :type image_group_number: int
        :param channel_offset: the offset in the array where the bytes for this image are found.
        :type channel_offset: int

        :return: (int, array.array()) or None

        """
        chunk = self._label_map[six.b("ImageDataSeq|%d!" % image_group_number)]
        data = self._read_chunk(chunk)
        # All images in the same image group share the same timestamp! So if you have complicated image data,
        # your timestamps may not be entirely accurate. Practically speaking though, they'll only be off by a few
        # seconds unless you're doing something super weird.
        timestamp = struct.unpack("d", data[:8])[0]
        image_group_data = array.array("H", data)
        image_data_start = 4 + channel_offset
        # The images for the various channels are interleaved within the same array. For example, the second image
        # of a four image group will be composed of bytes 2, 6, 10, etc. If you understand why someone would design
        # a data structure that way, please send the author of this library a message.
        image_data = image_group_data[image_data_start::self._channel_count]
        # Skip images that are all zeros! This is important, since NIS Elements creates blank "gap" images if you
        # don't have the same number of images each cycle. We discovered this because we only took GFP images every
        # other cycle to reduce phototoxicity, but NIS Elements still allocated memory as if we were going to take
        # them every cycle.
        if np.any(image_data):
            return timestamp, image_data
        return None

    @property
    def _dimensions(self):
        """
        While there are metadata values that represent a lot of what we want to capture, they seem to be unreliable.
        Sometimes certain elements don't exist, or change their data type randomly. However, the human-readable text
        is always there and in the same exact format, so we just parse that instead.

        :rtype: str

        """
        if self._dimension_text is None:
            for line in self.metadata[six.b('ImageTextInfo')][six.b('SLxImageTextInfo')].values():
                if six.b("Dimensions:") in line:
                    metadata = line
                    break
            else:
                raise ValueError("Could not parse metadata dimensions!")
            for line in metadata.split(six.b("\r\n")):
                if line.startswith(six.b("Dimensions:")):
                    self._dimension_text = line
                    break
            else:
                raise ValueError("Could not parse metadata dimensions!")
        if six.PY3:
            return self._dimension_text.decode("utf8")
        return self._dimension_text

    @property
    def _channels(self):
        """
        These are labels created by the NIS Elements user. Typically they may a short description of the filter cube
        used (e.g. "bright field", "GFP", etc.)

        :rtype: str

        """
        metadata = self.metadata[six.b('ImageMetadataSeq')][six.b('SLxPictureMetadata')][six.b('sPicturePlanes')]
        try:
            validity = self.metadata[six.b('ImageMetadata')][six.b('SLxExperiment')][six.b('ppNextLevelEx')][six.b('')][0][six.b('ppNextLevelEx')][six.b('')][0][six.b('pItemValid')]
        except KeyError:
            # If none of the channels have been deleted, there is no validity list, so we just make one
            validity = [True for _ in metadata]
        # Channel information is contained in dictionaries with the keys a0, a1...an where the number
        # indicates the order in which the channel is stored. So by sorting the dicts alphabetically
        # we get the correct order.
        for (label, chan), valid in zip(sorted(metadata[six.b('sPlaneNew')].items()), validity):
            if not valid:
                continue
            yield chan[six.b('sDescription')].decode("utf8")

    def _calculate_image_group_number(self, time_index, fov, z_level):
        """
        Images are grouped together if they share the same time index, field of view, and z-level.

        :type time_index: int
        :type fov: int
        :type z_level: int

        :rtype: int

        """
        return time_index * self._field_of_view_count * self._z_level_count + (fov * self._z_level_count + z_level)

    @property
    def _channel_offset(self):
        """
        Image data is interleaved for each image set. That is, if there are four images in a set, the first image
        will consist of pixels 1, 5, 9, etc, the second will be pixels 2, 6, 10, and so forth.

        :rtype: dict

        """
        channel_offset = {}
        for n, channel in enumerate(self._channels):
            channel_offset[channel] = n
        return channel_offset

    @property
    def _absolute_start(self):
        """
        The date and time when acquisition began.

        :rtype: datetime.datetime()

        """
        for line in self.metadata[six.b('ImageTextInfo')][six.b('SLxImageTextInfo')].values():
            line = line.decode("utf8")
            absolute_start_12 = None
            absolute_start_24 = None
            # ND2s seem to randomly switch between 12- and 24-hour representations.
            try:
                absolute_start_24 = datetime.strptime(line, "%m/%d/%Y  %H:%M:%S")
            except (TypeError, ValueError):
                pass
            try:
                absolute_start_12 = datetime.strptime(line, "%m/%d/%Y  %I:%M:%S %p")
            except (TypeError, ValueError):
                pass
            if not absolute_start_12 and not absolute_start_24:
                continue
            return absolute_start_12 if absolute_start_12 else absolute_start_24
        raise ValueError("This ND2 has no recorded start time. This is probably a bug.")

    @property
    def _channel_count(self):
        """
        The number of different channels used, including bright field.

        :rtype: int

        """
        pattern = r""".*?λ\((\d+)\).*?"""
        try:
            count = int(re.match(pattern, self._dimensions).group(1))
        except AttributeError as e:
            return 1
        else:
            return count

    @property
    def _field_of_view_count(self):
        """
        The metadata contains information about fields of view, but it contains it even if some fields
        of view were cropped. We can't find anything that states which fields of view are actually
        in the image data, so we have to calculate it. There probably is something somewhere, since
        NIS Elements can figure it out, but we haven't found it yet.

        :rtype: int

        """
        pattern = r""".*?XY\((\d+)\).*?"""
        try:
            count = int(re.match(pattern, self._dimensions).group(1))
        except AttributeError:
            return 1
        else:
            return count

    @property
    def _time_index_count(self):
        """
        The number of cycles.

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
    def _z_level_count(self):
        """
        The number of different levels in the Z-plane.

        :rtype: int

        """
        pattern = r""".*?Z\((\d+)\).*?"""
        try:
            count = int(re.match(pattern, self._dimensions).group(1))
        except AttributeError:
            return 1
        else:
            return count

    @property
    def _image_count(self):
        """
        The total number of images in the ND2. Warning: this may be inaccurate as it includes "gap" images.

        :rtype: int

        """
        return self.metadata[six.b('ImageAttributes')][six.b('SLxImageAttributes')][six.b('uiSequenceCount')]

    def _parse_metadata(self):
        """
        Reads all metadata.

        """
        for label in self._label_map.keys():
            if label.endswith(six.b("LV!")) or six.b("LV|") in label:
                data = self._read_chunk(self._label_map[label])
                stop = label.index(six.b("LV"))
                self.metadata[label[:stop]] = self._read_metadata(data, 1)

    def _read_map(self):
        """
        Every label ends with an exclamation point, however, we can't directly search for those to find all the labels
        as some of the bytes contain the value 33, which is the ASCII code for "!". So we iteratively find each label,
        grab the subsequent data (always 16 bytes long), advance to the next label and repeat.

        """
        self._file_handle.seek(-8, 2)
        chunk_map_start_location = struct.unpack("Q", self._file_handle.read(8))[0]
        self._file_handle.seek(chunk_map_start_location)
        raw_text = self._file_handle.read(-1)
        label_start = raw_text.index(Nd2Parser.CHUNK_MAP_START) + 32

        while True:
            data_start = raw_text.index(six.b("!"), label_start) + 1
            key = raw_text[label_start: data_start]
            location, length = struct.unpack("QQ", raw_text[data_start: data_start + 16])
            if key == Nd2Parser.CHUNK_MAP_END:
                # We've reached the end of the chunk map
                break
            self._label_map[key] = location
            label_start = data_start + 16

    def _read_chunk(self, chunk_location):
        """
        Gets the data for a given chunk pointer

        """
        self._file_handle.seek(chunk_location)
        # The chunk metadata is always 16 bytes long
        chunk_metadata = self._file_handle.read(16)
        header, relative_offset, data_length = struct.unpack("IIQ", chunk_metadata)
        if header != Nd2Parser.CHUNK_HEADER:
            raise ValueError("The ND2 file seems to be corrupted.")
        # We start at the location of the chunk metadata, skip over the metadata, and then proceed to the
        # start of the actual data field, which is at some arbitrary place after the metadata.
        self._file_handle.seek(chunk_location + 16 + relative_offset)
        return self._file_handle.read(data_length)

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
        while not value.endswith(six.b("\x00\x00")):
            # the string ends at the first instance of \x00\x00
            value += data.read(2)
        return value.decode("utf16")[:-1].encode("utf8")

    def _parse_char_array(self, data):
        array_length = struct.unpack("Q", data.read(8))[0]
        return array.array("B", data.read(array_length))

    def _parse_metadata_item(self, data):
        """
        Reads hierarchical data, analogous to a Python dict.

        """
        new_count, length = struct.unpack("<IQ", data.read(12))
        length -= data.tell() - self._cursor_position
        next_data_length = data.read(length)
        value = self._read_metadata(next_data_length, new_count)
        # Skip some offsets
        data.read(new_count * 8)
        return value

    def _get_value(self, data, data_type):
        """
        ND2s use various codes to indicate different data types, which we translate here.

        """
        parser = {1: self._parse_unsigned_char,
                  2: self._parse_unsigned_int,
                  3: self._parse_unsigned_int,
                  5: self._parse_unsigned_long,
                  6: self._parse_double,
                  8: self._parse_string,
                  9: self._parse_char_array,
                  11: self._parse_metadata_item}
        return parser[data_type](data)

    def _read_metadata(self, data, count):
        """
        Iterates over each element some section of the metadata and parses it.

        """
        data = six.BytesIO(data)
        metadata = {}
        for _ in range(count):
            self._cursor_position = data.tell()
            header = data.read(2)
            if not header:
                # We've reached the end of some hierarchy of data
                break
            if six.PY3:
                header = header.decode("utf8")
            data_type, name_length = map(ord, header)
            name = data.read(name_length * 2).decode("utf16")[:-1].encode("utf8")
            value = self._get_value(data, data_type)
            if name not in metadata.keys():
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