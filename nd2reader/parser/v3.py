# -*- coding: utf-8 -*-

import array
from datetime import datetime
from nd2reader.model.metadata import Metadata
from nd2reader.model.label import LabelMap
from nd2reader.parser.base import BaseParser
from nd2reader.driver.v3 import V3Driver
from nd2reader.common.v3 import read_chunk, read_array
import re
import six
import struct


class V3Parser(BaseParser):
    """ Parses ND2 files and creates a Metadata and driver object. """
    CHUNK_HEADER = 0xabeceda
    CHUNK_MAP_START = six.b("ND2 FILEMAP SIGNATURE NAME 0001!")
    CHUNK_MAP_END = six.b("ND2 CHUNK MAP SIGNATURE 0000001!")

    def __init__(self, fh):
        """
        :type fh:    file

        """
        self._fh = fh
        self._metadata = None
        self._label_map = None

    @property
    def metadata(self):
        """
        :rtype:    Metadata

        """
        if not self._metadata:
            self._parse_metadata()
        return self._metadata

    @property
    def driver(self):
        return V3Driver(self.metadata, self._label_map, self._fh)

    def _build_metadata_dict(self):
        self._label_map = self._build_label_map()
        raw_data = {"image_text_info": self._read_metadata(read_chunk(self._fh, self._label_map.image_text_info), 1),
                    "image_metadata_sequence": self._read_metadata(read_chunk(self._fh, self._label_map.image_metadata_sequence), 1),
                    "image_calibration": self._read_metadata(read_chunk(self._fh, self._label_map.image_calibration), 1),
                    "image_attributes": self._read_metadata(read_chunk(self._fh, self._label_map.image_attributes), 1),
                    "x_data": read_array(self._fh, 'double', self._label_map.x_data),
                    "y_data": read_array(self._fh, 'double', self._label_map.y_data),
                    "z_data": read_array(self._fh, 'double', self._label_map.z_data),
                    "roi_metadata": read_chunk(self._fh, self._label_map.roi_metadata),
                    "pfs_status": read_array(self._fh, 'int', self._label_map.pfs_status),
                    "pfs_offset": read_array(self._fh, 'int', self._label_map.pfs_offset),
                    "camera_exposure_time": read_array(self._fh, 'double', self._label_map.camera_exposure_time),
                    "camera_temp": map(lambda x: round(x * 100.0, 2), read_array(self._fh, 'double', self._label_map.camera_temp)),
                    "acquisition_times": map(lambda x: x / 1000.0, read_array(self._fh, 'double', self._label_map.acquisition_times)),
                    "lut_data": read_chunk(self._fh, self._label_map.lut_data),
                    "grabber_settings": read_chunk(self._fh, self._label_map.grabber_settings),
                    "custom_data": read_chunk(self._fh, self._label_map.custom_data),
                    "app_info": read_chunk(self._fh, self._label_map.app_info),
                    }
        if self._label_map.image_metadata:
            raw_data["image_metadata"] = self._read_metadata(read_chunk(self._fh, self._label_map.image_metadata), 1)

        return raw_data

    def _parse_metadata(self):
        """
        Reads all metadata and instantiates the Metadata object.

        """
        metadata_dict = self._build_metadata_dict()
        height = metadata_dict['image_attributes'][six.b('SLxImageAttributes')][six.b('uiHeight')]
        width = metadata_dict['image_attributes'][six.b('SLxImageAttributes')][six.b('uiWidth')]
        channels = self._parse_channels(metadata_dict)
        date = self._parse_date(metadata_dict)
        fields_of_view = self._parse_fields_of_view(metadata_dict)
        frames = self._parse_frames(metadata_dict)
        z_levels = self._parse_z_levels(metadata_dict)
        total_images_per_channel = self._parse_total_images_per_channel(metadata_dict)
        self._metadata = Metadata(height, width, channels, date, fields_of_view, frames, z_levels, total_images_per_channel)

    def _parse_date(self, metadata_dict):
        """
        The date and time when acquisition began.

        :type metadata_dict:    dict
        :rtype: datetime.datetime() or None

        """
        for line in metadata_dict['image_text_info'][six.b('SLxImageTextInfo')].values():
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
        return None

    def _parse_channels(self, metadata_dict):
        """
        These are labels created by the NIS Elements user. Typically they may a short description of the filter cube
        used (e.g. "bright field", "GFP", etc.)

        :type metadata_dict:    dict
        :rtype: list

        """
        channels = []
        metadata = metadata_dict['image_metadata_sequence'][six.b('SLxPictureMetadata')][six.b('sPicturePlanes')]
        try:
            validity = metadata_dict['image_metadata'][six.b('SLxExperiment')][six.b('ppNextLevelEx')][six.b('')][0][six.b('ppNextLevelEx')][six.b('')][0][six.b('pItemValid')]
        except KeyError:
            # If none of the channels have been deleted, there is no validity list, so we just make one
            validity = [True for _ in metadata]
        # Channel information is contained in dictionaries with the keys a0, a1...an where the number
        # indicates the order in which the channel is stored. So by sorting the dicts alphabetically
        # we get the correct order.
        for (label, chan), valid in zip(sorted(metadata[six.b('sPlaneNew')].items()), validity):
            if not valid:
                continue
            channels.append(chan[six.b('sDescription')].decode("utf8"))
        return channels

    def _parse_fields_of_view(self, metadata_dict):
        """
        The metadata contains information about fields of view, but it contains it even if some fields
        of view were cropped. We can't find anything that states which fields of view are actually
        in the image data, so we have to calculate it. There probably is something somewhere, since
        NIS Elements can figure it out, but we haven't found it yet.

        :type metadata_dict:    dict
        :rtype:    list

        """
        return self._parse_dimension(r""".*?XY\((\d+)\).*?""", metadata_dict)

    def _parse_frames(self, metadata_dict):
        """
        The number of cycles.

        :type metadata_dict:    dict
        :rtype:     list

        """
        return self._parse_dimension(r""".*?T'?\((\d+)\).*?""", metadata_dict)

    def _parse_z_levels(self, metadata_dict):
        """
        The different levels in the Z-plane. Just a sequence from 0 to n.

        :type metadata_dict:    dict
        :rtype:    list

        """
        return self._parse_dimension(r""".*?Z\((\d+)\).*?""", metadata_dict)

    def _parse_dimension_text(self, metadata_dict):
        """
        While there are metadata values that represent a lot of what we want to capture, they seem to be unreliable.
        Sometimes certain elements don't exist, or change their data type randomly. However, the human-readable text
        is always there and in the same exact format, so we just parse that instead.

        :type metadata_dict:    dict
        :rtype:    str

        """
        for line in metadata_dict['image_text_info'][six.b('SLxImageTextInfo')].values():
            if six.b("Dimensions:") in line:
                metadata = line
                break
        else:
            return six.b("")
        for line in metadata.split(six.b("\r\n")):
            if line.startswith(six.b("Dimensions:")):
                dimension_text = line
                break
        else:
            return six.b("")
        return dimension_text

    def _parse_dimension(self, pattern, metadata_dict):
        """
        :param pattern:    a valid regex pattern
        :type pattern:    str
        :type metadata_dict:    dict

        :rtype:    list of int

        """
        dimension_text = self._parse_dimension_text(metadata_dict)
        if six.PY3:
            dimension_text = dimension_text.decode("utf8")
        match = re.match(pattern, dimension_text)
        if not match:
            return [0]
        count = int(match.group(1))
        return list(range(count))

    def _parse_total_images_per_channel(self, metadata_dict):
        """
        The total number of images per channel. Warning: this may be inaccurate as it includes "gap" images.

        :type metadata_dict:    dict
        :rtype: int

        """
        return metadata_dict['image_attributes'][six.b('SLxImageAttributes')][six.b('uiSequenceCount')]

    def _build_label_map(self):
        """
        Every label ends with an exclamation point, however, we can't directly search for those to find all the labels
        as some of the bytes contain the value 33, which is the ASCII code for "!". So we iteratively find each label,
        grab the subsequent data (always 16 bytes long), advance to the next label and repeat.

        :rtype: LabelMap

        """
        self._fh.seek(-8, 2)
        chunk_map_start_location = struct.unpack("Q", self._fh.read(8))[0]
        self._fh.seek(chunk_map_start_location)
        raw_text = self._fh.read(-1)
        return LabelMap(raw_text)

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
