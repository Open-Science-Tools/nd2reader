# -*- coding: utf-8 -*-

import array
import numpy as np
import struct
import six
from nd2reader.model.image import Image
from nd2reader.parser.v3 import read_chunk


class V3Driver(object):
    def __init__(self, metadata, label_map, file_handle):
        self._metadata = metadata
        self._label_map = label_map
        self._file_handle = file_handle
        
    def _calculate_field_of_view(self, frame_number):
        images_per_cycle = len(self._metadata.z_levels) * len(self._metadata.channels)
        return int((frame_number - (frame_number % images_per_cycle)) / images_per_cycle) % len(self._metadata.fields_of_view)

    def _calculate_channel(self, frame_number):
        return self._metadata.channels[frame_number % len(self._metadata.channels)]

    def _calculate_z_level(self, frame_number):
        return self._metadata.z_levels[int(((frame_number - (frame_number % len(self._metadata.channels))) / len(self._metadata.channels)) % len(self._metadata.z_levels))]

    def _calculate_image_group_number(self, time_index, fov, z_level):
        """
        Images are grouped together if they share the same time index, field of view, and z-level.

        :type time_index: int
        :type fov: int
        :type z_level: int

        :rtype: int

        """
        return time_index * len(self._metadata.fields_of_view) * len(self._metadata.z_levels) + (fov * len(self._metadata.z_levels) + z_level)

    def _calculate_frame_number(self, image_group_number, fov, z_level):
        return (image_group_number - (fov * len(self._metadata.z_levels) + z_level)) / (len(self._metadata.fields_of_view) * len(self._metadata.z_levels))

    def get_image(self, index):
        channel_offset = index % len(self._metadata.channels)
        fov = self._calculate_field_of_view(index)
        channel = self._calculate_channel(index)
        z_level = self._calculate_z_level(index)
        image_group_number = int(index / len(self._metadata.channels))
        frame_number = self._calculate_frame_number(image_group_number, fov, z_level)
        timestamp, image = self._get_raw_image_data(image_group_number, channel_offset, self._metadata.height, self._metadata.width)
        image.add_params(timestamp, frame_number, fov, channel, z_level)
        return image

    @property
    def _channel_offset(self):
        """
        Image data is interleaved for each image set. That is, if there are four images in a set, the first image
        will consist of pixels 1, 5, 9, etc, the second will be pixels 2, 6, 10, and so forth.

        :rtype: dict

        """
        channel_offset = {}
        for n, channel in enumerate(self._metadata.channels):
            channel_offset[channel] = n
        return channel_offset

    def _get_raw_image_data(self, image_group_number, channel_offset, height, width):
        """
        Reads the raw bytes and the timestamp of an image.

        :param image_group_number: groups are made of images with the same time index, field of view and z-level.
        :type image_group_number: int
        :param channel_offset: the offset in the array where the bytes for this image are found.
        :type channel_offset: int

        :return: (int, array.array()) or None

        """
        chunk = self._label_map[six.b("ImageDataSeq|%d!" % image_group_number)]
        data = read_chunk(self._file_handle, chunk)
        # All images in the same image group share the same timestamp! So if you have complicated image data,
        # your timestamps may not be entirely accurate. Practically speaking though, they'll only be off by a few
        # seconds unless you're doing something super weird.
        timestamp = struct.unpack("d", data[:8])[0]
        image_group_data = array.array("H", data)
        image_data_start = 4 + channel_offset
        # The images for the various channels are interleaved within the same array. For example, the second image
        # of a four image group will be composed of bytes 2, 6, 10, etc. If you understand why someone would design
        # a data structure that way, please send the author of this library a message.
        image_data = np.reshape(image_group_data[image_data_start::len(self._metadata.channels)], (height, width))
        # Skip images that are all zeros! This is important, since NIS Elements creates blank "gap" images if you
        # don't have the same number of images each cycle. We discovered this because we only took GFP images every
        # other cycle to reduce phototoxicity, but NIS Elements still allocated memory as if we were going to take
        # them every cycle.
        if np.any(image_data):
            return timestamp, Image(image_data)
        return None
