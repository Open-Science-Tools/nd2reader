# -*- coding: utf-8 -*-
import struct

import array
import six
from pims import Frame
import numpy as np

from nd2reader.common import get_version, read_chunk
from nd2reader.exceptions import InvalidVersionError, NoImageError
from nd2reader.label_map import LabelMap
from nd2reader.raw_metadata import RawMetadata


class ND2Parser(object):
    """ Parses ND2 files and creates a Metadata and driver object. """
    CHUNK_HEADER = 0xabeceda
    CHUNK_MAP_START = six.b("ND2 FILEMAP SIGNATURE NAME 0001!")
    CHUNK_MAP_END = six.b("ND2 CHUNK MAP SIGNATURE 0000001!")

    supported_file_versions = {(3, None): True}

    def __init__(self, fh):
        """
        :type fh:    file

        """
        self._fh = fh
        self._label_map = None
        self._raw_metadata = None
        self.metadata = None

        # First check the file version
        self._check_version_supported()

        # Parse the metadata
        self._parse_metadata()

    def calculate_image_properties(self, index):
        """
        Calculate FOV, channels and z_levels
        :param index:
        :return:
        """
        field_of_view = self._calculate_field_of_view(index)
        channel = self._calculate_channel(index)
        z_level = self._calculate_z_level(index)
        return field_of_view, channel, z_level

    def get_image(self, index):
        """
        Creates an Image object and adds its metadata, based on the index (which is simply the order in which the image
        was acquired). May return None if the ND2 contains multiple channels and not all were taken in each cycle (for
        example, if you take bright field images every minute, and GFP images every five minutes, there will be some
        indexes that do not contain an image. The reason for this is complicated, but suffice it to say that we hope to
        eliminate this possibility in future releases. For now, you'll need to check if your image is None if you're
        doing anything out of the ordinary.

        :type index:    int
        :rtype:    Image or None

        """
        field_of_view, channel, z_level = self.calculate_image_properties(index)
        channel_offset = index % len(self.metadata["channels"])
        image_group_number = int(index / len(self.metadata["channels"]))
        frame_number = self._calculate_frame_number(image_group_number, field_of_view, z_level)
        try:
            timestamp, image = self._get_raw_image_data(image_group_number, channel_offset, self.metadata["height"],
                                                        self.metadata["width"])
        except NoImageError:
            return None
        else:
            image.add_params(index, timestamp, frame_number, field_of_view, channel, z_level)
            return image

    def get_image_by_attributes(self, frame_number, field_of_view, channel_name, z_level, height, width):
        """
        Attempts to get Image based on attributes alone.

        :type frame_number:    int
        :type field_of_view:    int
        :type channel_name:    str
        :type z_level:    int
        :type height:    int
        :type width:    int

        :rtype: Image or None
        """
        image_group_number = self._calculate_image_group_number(frame_number, field_of_view, z_level)
        try:
            timestamp, raw_image_data = self._get_raw_image_data(image_group_number, self._channel_offset[channel_name],
                                                                 height, width)
            image = Frame(raw_image_data, frame_no=frame_number, metadata=self._get_frame_metadata())
        except (TypeError, NoImageError):
            return None
        else:
            return image

    def get_dtype_from_metadata(self):
        """
        Determine the data type from the metadata.
        :return:
        """
        bit_depth = self._raw_metadata.image_attributes[six.b('SLxImageAttributes')][six.b('uiBpcInMemory')]
        dtype = np.float64
        if bit_depth <= 16:
            dtype = np.float16
        elif bit_depth <= 32:
            dtype = np.float32

        return dtype

    def _check_version_supported(self):
        """
        Checks if the ND2 file version is supported by this reader.
        :return:
        """
        major_version, minor_version = get_version(self._fh)
        supported = self.supported_file_versions.get((major_version, minor_version)) or \
                    self.supported_file_versions.get((major_version, None))

        if not supported:
            raise InvalidVersionError("No parser is available for that version.")

        return supported

    def _parse_metadata(self):
        """
        Reads all metadata and instantiates the Metadata object.

        """
        # Retrieve raw metadata from the label mapping
        self._label_map = self._build_label_map()
        self._raw_metadata = RawMetadata(self._fh, self._label_map)
        self.metadata = self._raw_metadata.__dict__

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

    def _calculate_field_of_view(self, index):
        """
        Determines what field of view was being imaged for a given image.

        :type index:    int
        :rtype:    int

        """
        images_per_cycle = len(self.metadata["z_levels"]) * len(self.metadata["channels"])
        return int((index - (index % images_per_cycle)) / images_per_cycle) % len(self.metadata["fields_of_view"])

    def _calculate_channel(self, index):
        """
        Determines what channel a particular image is.

        :type index:    int
        :rtype:    str

        """
        return self.metadata["channels"][index % len(self.metadata["channels"])]

    def _calculate_z_level(self, index):
        """
        Determines the plane in the z-axis a given image was taken in. In the future, this will be replaced with the
        actual offset in micrometers.

        :type index:    int
        :rtype:    int
        """
        return self.metadata["z_levels"][int(
            ((index - (index % len(self.metadata["channels"]))) / len(self.metadata["channels"])) % len(
                self.metadata["z_levels"]))]

    def _calculate_image_group_number(self, frame_number, fov, z_level):
        """
        Images are grouped together if they share the same time index, field of view, and z-level.

        :type frame_number: int
        :type fov: int
        :type z_level: int

        :rtype: int

        """
        return frame_number * len(self.metadata["fields_of_view"]) * len(self.metadata["z_levels"]) + (
            fov * len(self.metadata["z_levels"]) + z_level)

    def _calculate_frame_number(self, image_group_number, field_of_view, z_level):
        """
        Images are in the same frame if they share the same group number and field of view and are taken sequentially.

        :type image_group_number:    int
        :type field_of_view:    int
        :type z_level:    int

        :rtype:    int

        """
        return (image_group_number - (field_of_view * len(self.metadata["z_levels"]) + z_level)) / (
            len(self.metadata["fields_of_view"]) * len(self.metadata["z_levels"]))

    @property
    def _channel_offset(self):
        """
        Image data is interleaved for each image set. That is, if there are four images in a set, the first image
        will consist of pixels 1, 5, 9, etc, the second will be pixels 2, 6, 10, and so forth.

        :rtype: dict

        """
        return {channel: n for n, channel in enumerate(self.metadata["channels"])}

    def _get_raw_image_data(self, image_group_number, channel_offset, height, width):
        """
        Reads the raw bytes and the timestamp of an image.

        :param image_group_number: groups are made of images with the same time index, field of view and z-level
        :type image_group_number: int
        :param channel_offset: the offset in the array where the bytes for this image are found
        :type channel_offset: int

        :rtype:    (int, Image)
        :raises:    NoImageError

        """
        chunk = self._label_map.get_image_data_location(image_group_number)
        data = read_chunk(self._fh, chunk)
        # print("data", data, "that was data")
        # All images in the same image group share the same timestamp! So if you have complicated image data,
        # your timestamps may not be entirely accurate. Practically speaking though, they'll only be off by a few
        # seconds unless you're doing something super weird.
        timestamp = struct.unpack("d", data[:8])[0]
        image_group_data = array.array("H", data)
        image_data_start = 4 + channel_offset

        # The images for the various channels are interleaved within the same array. For example, the second image
        # of a four image group will be composed of bytes 2, 6, 10, etc. If you understand why someone would design
        # a data structure that way, please send the author of this library a message.
        number_of_true_channels = int((len(image_group_data) - 4) / (height * width))
        image_data = np.reshape(image_group_data[image_data_start::number_of_true_channels], (height, width))

        # Skip images that are all zeros! This is important, since NIS Elements creates blank "gap" images if you
        # don't have the same number of images each cycle. We discovered this because we only took GFP images every
        # other cycle to reduce phototoxicity, but NIS Elements still allocated memory as if we were going to take
        # them every cycle.
        if np.any(image_data):
            return timestamp, Frame(image_data)
        raise NoImageError

    def _get_frame_metadata(self):
        """
        Get the metadata for one frame
        :return:
        """
        return self.metadata
