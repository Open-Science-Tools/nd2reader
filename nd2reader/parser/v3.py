# -*- coding: utf-8 -*-

import array
from datetime import datetime
from nd2reader.model.metadata import Metadata
from nd2reader.parser.parser import BaseParser
import re
import six
import struct


class V3Parser(BaseParser):
    """ Parses ND2 files and creates a Metadata and ImageReader object. """
    CHUNK_HEADER = 0xabeceda
    CHUNK_MAP_START = six.b("ND2 FILEMAP SIGNATURE NAME 0001!")
    CHUNK_MAP_END = six.b("ND2 CHUNK MAP SIGNATURE 0000001!")

    def __init__(self, filename):
        self._filename = filename
        self._fh = None
        self._metadata = None

    @property
    def metadata(self):
        if not self._metadata:
            self._parse_metadata()
        return self.metadata

    @property
    def driver(self):
        raise NotImplementedError

    def _parse_metadata(self):
        """
        Reads all metadata.

        """
        metadata_dict = {}
        label_map = self._build_label_map()
        for label in label_map.keys():
            if label.endswith(six.b("LV!")) or six.b("LV|") in label:
                data = self._read_chunk(label_map[label])
                stop = label.index(six.b("LV"))
                metadata_dict[label[:stop]] = self._read_metadata(data, 1)

        channels = self._parse_channels(metadata_dict)
        date = self._parse_fields_of_view(metadata_dict)
        fields_of_view = self._parse_fields_of_view(metadata_dict)
        frames = self._parse_frames(metadata_dict)
        z_levels = self._parse_z_levels(metadata_dict)
        self._metadata = Metadata(channels, date, fields_of_view, frames, z_levels)

    def _parse_date(self, metadata_dict):
        """
        The date and time when acquisition began.

        :rtype: datetime.datetime()

        """
        for line in metadata_dict[six.b('ImageTextInfo')][six.b('SLxImageTextInfo')].values():
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

    def _parse_channels(self, metadata_dict):
        """
        These are labels created by the NIS Elements user. Typically they may a short description of the filter cube
        used (e.g. "bright field", "GFP", etc.)

        :rtype: list

        """
        channels = []
        metadata = metadata_dict[six.b('ImageMetadataSeq')][six.b('SLxPictureMetadata')][six.b('sPicturePlanes')]
        try:
            validity = metadata_dict[six.b('ImageMetadata')][six.b('SLxExperiment')][six.b('ppNextLevelEx')][six.b('')][0][six.b('ppNextLevelEx')][six.b('')][0][six.b('pItemValid')]
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

        :rtype: list

        """
        return self._parse_dimension(r""".*?XY\((\d+)\).*?""", metadata_dict)

    def _parse_frames(self, metadata_dict):
        """
        The number of cycles.

        :rtype:     list

        """
        return self._parse_dimension(r""".*?T'\((\d+)\).*?""", metadata_dict)

    def _parse_z_levels(self, metadata_dict):
        """
        The different levels in the Z-plane. Just a sequence from 0 to n.

        :rtype: list

        """
        return self._parse_dimension(r""".*?Z\((\d+)\).*?""", metadata_dict)

    def _get_file_handle(self):
        if self._fh is None:
            self._fh = open(self._filename, "rb")
        return self._fh

    def _parse_dimension_text(self, metadata_dict):
        """
        While there are metadata values that represent a lot of what we want to capture, they seem to be unreliable.
        Sometimes certain elements don't exist, or change their data type randomly. However, the human-readable text
        is always there and in the same exact format, so we just parse that instead.

        :rtype: str

        """
        for line in metadata_dict[six.b('ImageTextInfo')][six.b('SLxImageTextInfo')].values():
            if six.b("Dimensions:") in line:
                metadata = line
                break
        else:
            raise ValueError("Could not parse metadata dimensions!")
        for line in metadata.split(six.b("\r\n")):
            if line.startswith(six.b("Dimensions:")):
                dimension_text = line
                break
        else:
            raise ValueError("Could not parse metadata dimensions!")
        return dimension_text

    def _parse_dimension(self, pattern, metadata_dict):
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

        :rtype: int

        """
        return metadata_dict[six.b('ImageAttributes')][six.b('SLxImageAttributes')][six.b('uiSequenceCount')]

    def _build_label_map(self):
        """
        Every label ends with an exclamation point, however, we can't directly search for those to find all the labels
        as some of the bytes contain the value 33, which is the ASCII code for "!". So we iteratively find each label,
        grab the subsequent data (always 16 bytes long), advance to the next label and repeat.

        :rtype: dict

        """
        label_map = {}
        self._get_file_handle().seek(-8, 2)
        chunk_map_start_location = struct.unpack("Q", self._get_file_handle().read(8))[0]
        self._get_file_handle().seek(chunk_map_start_location)
        raw_text = self._get_file_handle().read(-1)
        label_start = raw_text.index(V3Parser.CHUNK_MAP_START) + 32

        while True:
            data_start = raw_text.index(six.b("!"), label_start) + 1
            key = raw_text[label_start: data_start]
            location, length = struct.unpack("QQ", raw_text[data_start: data_start + 16])
            if key == V3Parser.CHUNK_MAP_END:
                # We've reached the end of the chunk map
                break
            label_map[key] = location
            label_start = data_start + 16
        return label_map

    def _read_chunk(self, chunk_location):
        """
        Gets the data for a given chunk pointer

        """
        self._get_file_handle().seek(chunk_location)
        # The chunk metadata is always 16 bytes long
        chunk_metadata = self._get_file_handle().read(16)
        header, relative_offset, data_length = struct.unpack("IIQ", chunk_metadata)
        if header != V3Parser.CHUNK_HEADER:
            raise ValueError("The ND2 file seems to be corrupted.")
        # We start at the location of the chunk metadata, skip over the metadata, and then proceed to the
        # start of the actual data field, which is at some arbitrary place after the metadata.
        self._get_file_handle().seek(chunk_location + 16 + relative_offset)
        val = self._get_file_handle().read(data_length)
        print("**************************")
        print(type(val))
        return val

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
