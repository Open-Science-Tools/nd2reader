# -*- coding: utf-8 -*-

from datetime import datetime
from nd2reader.model.metadata import Metadata
from nd2reader.model.label import LabelMap
from nd2reader.model.roi import Roi
from nd2reader.parser.base import BaseParser
from nd2reader.driver.v3 import V3Driver
from nd2reader.common.v3 import read_chunk, read_array, read_metadata
import re
import six
import struct
import xmltodict


def ignore_missing(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return None

    return wrapper


class V3RawMetadata(object):
    def __init__(self, fh, label_map):
        self._fh = fh
        self._label_map = label_map

    @property
    @ignore_missing
    def image_text_info(self):
        return read_metadata(read_chunk(self._fh, self._label_map.image_text_info), 1)

    @property
    @ignore_missing
    def image_metadata_sequence(self):
        return read_metadata(read_chunk(self._fh, self._label_map.image_metadata_sequence), 1)

    @property
    @ignore_missing
    def image_calibration(self):
        return read_metadata(read_chunk(self._fh, self._label_map.image_calibration), 1)

    @property
    @ignore_missing
    def image_attributes(self):
        return read_metadata(read_chunk(self._fh, self._label_map.image_attributes), 1)

    @property
    @ignore_missing
    def x_data(self):
        return read_array(self._fh, 'double', self._label_map.x_data)

    @property
    @ignore_missing
    def y_data(self):
        return read_array(self._fh, 'double', self._label_map.y_data)

    @property
    @ignore_missing
    def z_data(self):
        return read_array(self._fh, 'double', self._label_map.z_data)

    @property
    @ignore_missing
    def roi_metadata(self):
        return read_metadata(read_chunk(self._fh, self._label_map.roi_metadata), 1)

    @property
    @ignore_missing
    def pfs_status(self):
        return read_array(self._fh, 'int', self._label_map.pfs_status)

    @property
    @ignore_missing
    def pfs_offset(self):
        return read_array(self._fh, 'int', self._label_map.pfs_offset)

    @property
    @ignore_missing
    def camera_exposure_time(self):
        return read_array(self._fh, 'double', self._label_map.camera_exposure_time)

    @property
    @ignore_missing
    def lut_data(self):
        return xmltodict.parse(read_chunk(self._fh, self._label_map.lut_data))

    @property
    @ignore_missing
    def grabber_settings(self):
        return xmltodict.parse(read_chunk(self._fh, self._label_map.grabber_settings))

    @property
    @ignore_missing
    def custom_data(self):
        return xmltodict.parse(read_chunk(self._fh, self._label_map.custom_data))

    @property
    @ignore_missing
    def app_info(self):
        return xmltodict.parse(read_chunk(self._fh, self._label_map.app_info))

    @property
    @ignore_missing
    def camera_temp(self):
        camera_temp = read_array(self._fh, 'double', self._label_map.camera_temp)
        if camera_temp:
            for temp in map(lambda x: round(x * 100.0, 2), camera_temp):
                yield temp

    @property
    @ignore_missing
    def acquisition_times(self):
        acquisition_times = read_array(self._fh, 'double', self._label_map.acquisition_times)
        if acquisition_times:
            for acquisition_time in map(lambda x: x / 1000.0, acquisition_times):
                yield acquisition_time

    @property
    @ignore_missing
    def image_metadata(self):
        if self._label_map.image_metadata:
            return read_metadata(read_chunk(self._fh, self._label_map.image_metadata), 1)


class V3Parser(BaseParser):
    """ Parses ND2 files and creates a Metadata and driver object. """
    CHUNK_HEADER = 0xabeceda
    CHUNK_MAP_START = six.b("ND2 FILEMAP SIGNATURE NAME 0001!")
    CHUNK_MAP_END = six.b("ND2 CHUNK MAP SIGNATURE 0000001!")

    def __init__(self, fh):
        """
        :type fh:    file

        """
        if six.PY3:
            super().__init__(fh)
        else:
            super(V3Parser, self).__init__(fh)
        self._label_map = self._build_label_map()
        self.raw_metadata = V3RawMetadata(self._fh, self._label_map)
        self._parse_metadata()
        self._parse_roi_metadata()

    @property
    def driver(self):
        """
        Provides an object that knows how to look up and read images based on an index.

        """
        return V3Driver(self.metadata, self._label_map, self._fh)

    def _parse_metadata(self):
        """
        Reads all metadata and instantiates the Metadata object.

        """
        height = self.raw_metadata.image_attributes[six.b('SLxImageAttributes')][six.b('uiHeight')]
        width = self.raw_metadata.image_attributes[six.b('SLxImageAttributes')][six.b('uiWidth')]
        date = self._parse_date(self.raw_metadata)
        fields_of_view = self._parse_fields_of_view(self.raw_metadata)
        frames = self._parse_frames(self.raw_metadata)
        z_levels = self._parse_z_levels(self.raw_metadata)
        total_images_per_channel = self._parse_total_images_per_channel(self.raw_metadata)
        channels = self._parse_channels(self.raw_metadata)
        pixel_microns = self.raw_metadata.image_calibration.get(six.b('SLxCalibration'), {}).get(six.b('dCalibration'))
        self.metadata = Metadata(height, width, channels, date, fields_of_view, frames, z_levels,
                                 total_images_per_channel, pixel_microns)

    def _parse_date(self, raw_metadata):
        """
        The date and time when acquisition began.

        :type raw_metadata:    V3RawMetadata
        :rtype: datetime.datetime() or None

        """
        for line in raw_metadata.image_text_info[six.b('SLxImageTextInfo')].values():
            line = line.decode("utf8")
            # ND2s seem to randomly switch between 12- and 24-hour representations.
            absolute_start_24 = self._parse_date_24h(line)
            absolute_start_12 = self._parse_date_12h(line)
            if not absolute_start_12 and not absolute_start_24:
                continue
            return absolute_start_12 if absolute_start_12 else absolute_start_24
        return None

    @staticmethod
    def _parse_date_12h(line):
        try:
            absolute_start_12 = datetime.strptime(line, "%m/%d/%Y  %I:%M:%S %p")
            return absolute_start_12
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_date_24h(line):
        try:
            absolute_start_24 = datetime.strptime(line, "%m/%d/%Y  %H:%M:%S")
            return absolute_start_24
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_channels(raw_metadata):
        """
        These are labels created by the NIS Elements user. Typically they may a short description of the filter cube
        used (e.g. "bright field", "GFP", etc.)

        :type raw_metadata:    V3RawMetadata
        :rtype: list

        """
        channels = []
        metadata = raw_metadata.image_metadata_sequence[six.b('SLxPictureMetadata')][six.b('sPicturePlanes')]
        try:
            validity = raw_metadata.image_metadata[six.b('SLxExperiment')][six.b('ppNextLevelEx')][six.b('')][0][
                six.b('ppNextLevelEx')][six.b('')][0][six.b('pItemValid')]
        except (KeyError, TypeError):
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

    def _parse_fields_of_view(self, raw_metadata):
        """
        The metadata contains information about fields of view, but it contains it even if some fields
        of view were cropped. We can't find anything that states which fields of view are actually
        in the image data, so we have to calculate it. There probably is something somewhere, since
        NIS Elements can figure it out, but we haven't found it yet.

        :type raw_metadata:    V3RawMetadata
        :rtype:    list

        """
        return self._parse_dimension(r""".*?XY\((\d+)\).*?""", raw_metadata)

    def _parse_frames(self, raw_metadata):
        """
        The number of cycles.

        :type raw_metadata:    V3RawMetadata
        :rtype:     list

        """
        return self._parse_dimension(r""".*?T'?\((\d+)\).*?""", raw_metadata)

    def _parse_z_levels(self, raw_metadata):
        """
        The different levels in the Z-plane. Just a sequence from 0 to n.

        :type raw_metadata:    V3RawMetadata
        :rtype:    list

        """
        return self._parse_dimension(r""".*?Z\((\d+)\).*?""", raw_metadata)

    @staticmethod
    def _parse_dimension_text(raw_metadata):
        """
        While there are metadata values that represent a lot of what we want to capture, they seem to be unreliable.
        Sometimes certain elements don't exist, or change their data type randomly. However, the human-readable text
        is always there and in the same exact format, so we just parse that instead.

        :type raw_metadata:    V3RawMetadata
        :rtype:    str

        """
        dimension_text = six.b("")
        textinfo = raw_metadata.image_text_info[six.b('SLxImageTextInfo')].values()

        for line in textinfo:
            if six.b("Dimensions:") in line:
                entries = line.split(six.b("\r\n"))
                for entry in entries:
                    if entry.startswith(six.b("Dimensions:")):
                        return entry

        return dimension_text

    def _parse_dimension(self, pattern, raw_metadata):
        """
        :param pattern:    a valid regex pattern
        :type pattern:    str
        :type raw_metadata:    V3RawMetadata

        :rtype:    list of int

        """
        dimension_text = self._parse_dimension_text(raw_metadata)
        if six.PY3:
            dimension_text = dimension_text.decode("utf8")
        match = re.match(pattern, dimension_text)
        if not match:
            return [0]
        count = int(match.group(1))
        return list(range(count))

    @staticmethod
    def _parse_total_images_per_channel(raw_metadata):
        """
        The total number of images per channel. Warning: this may be inaccurate as it includes "gap" images.

        :type raw_metadata:    V3RawMetadata
        :rtype: int

        """
        return raw_metadata.image_attributes[six.b('SLxImageAttributes')][six.b('uiSequenceCount')]

    def _parse_roi_metadata(self):
        """
        Parse the raw ROI metadata.
        :return:
        """
        if not six.b('RoiMetadata_v1') in self.raw_metadata.roi_metadata:
            self.roi_metadata = None
            return

        raw_roi_data = self.raw_metadata.roi_metadata[six.b('RoiMetadata_v1')]

        number_of_rois = raw_roi_data[six.b('m_vectGlobal_Size')]

        roi_objects = []
        for i in range(number_of_rois):
            current_roi = raw_roi_data[six.b('m_vectGlobal_%d' % i)]
            roi_objects.append(Roi(current_roi, self.metadata))

        self.roi_metadata = roi_objects

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
