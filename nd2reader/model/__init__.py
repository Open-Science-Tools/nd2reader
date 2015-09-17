# -*- coding: utf-8 -*-

import collections
import numpy as np
import logging

log = logging.getLogger(__name__)


class Image(object):
    def __init__(self, timestamp, frame_number, raw_array, field_of_view, channel, z_level, height, width):
        """
        A wrapper around the raw pixel data of an image.

        :param timestamp: The frame number relative to the .
        :type timestamp: int
        :param timestamp: The number of milliseconds after the beginning of the acquisition that this image was taken.
        :type timestamp: int
        :param raw_array: The raw sequence of bytes that represents the image.
        :type raw_array: array.array()
        :param field_of_view: The label for the place in the XY-plane where this image was taken.
        :type field_of_view: int
        :param channel: The name of the color of this image
        :type channel: str
        :param z_level: The label for the location in the Z-plane where this image was taken.
        :type z_level: int
        :param height: The height of the image in pixels.
        :type height: int
        :param width: The width of the image in pixels.
        :type width: int

        """
        self._timestamp = timestamp
        self._frame_number = int(frame_number)
        self._raw_data = raw_array
        self._field_of_view = field_of_view
        self._channel = channel
        self._z_level = z_level
        self._height = height
        self._width = width
        self._data = None

    def __repr__(self):
        return "\n".join(["<ND2 Image>",
                          "%sx%s (HxW)" % (self._height, self._width),
                          "Timestamp: %s" % self.timestamp,
                          "Frame: %s" % self._frame_number,
                          "Field of View: %s" % self.field_of_view,
                          "Channel: %s" % self.channel,
                          "Z-Level: %s" % self.z_level,
                          ])

    @property
    def data(self):
        """
        The actual image data.

        :rtype np.array()

        """
        if self._data is None:
            # The data is just a 1-dimensional array originally.
            # We convert it to a 2D image here.
            self._data = np.reshape(self._raw_data, (self._height, self._width))
        return self._data

    @property
    def field_of_view(self):
        """
        Which of the fixed locations this image was taken at.

        :rtype int:

        """
        return self._field_of_view

    @property
    def timestamp(self):
        """
        The number of seconds after the beginning of the acquisition that the image was taken. Note that for a given
        field of view and z-level offset, if you have images of multiple channels, they will all be given the same
        timestamp. No, this doesn't make much sense. But that's how ND2s are structured, so if your experiment depends
        on millisecond accuracy, you need to find an alternative imaging system.

        :rtype float:

        """
        return self._timestamp / 1000.0

    @property
    def frame_number(self):
        return self._frame_number

    @property
    def channel(self):
        """
        The name of the filter used to acquire this image. These are user-supplied in NIS Elements.

        :rtype str:

        """
        return self._channel

    @property
    def z_level(self):
        """
        The vertical offset of the image. These are simple integers starting from 0, where the 0 is the lowest
        z-level and each subsequent level incremented by 1.

        For example, if you acquired images at -3 µm, 0 µm, and +3 µm, your z-levels would be:

        -3 µm: 0
        0 µm: 1
        +3 µm: 2

        :rtype int:

        """
        return self._z_level


class ImageSet(object):
    """
    A group of images that were taken at roughly the same time.

    """
    def __init__(self):
        self._images = collections.defaultdict(dict)

    def __len__(self):
        """ The number of images in the image set. """
        return sum([len(channel) for channel in self._images.values()])

    def __repr__(self):
        return "\n".join(["<ND2 Image Set>",
                          "Image count: %s" % len(self)])

    def get(self, channel, z_level=0):
        """
        Retrieve an image with a given channel and z-level. For most users, z_level will always be 0.

        :type channel:  str
        :type z_level:  int

        """
        return self._images.get(channel).get(z_level)

    def add(self, image):
        """
        Stores an image.

        :type image:    nd2reader.model.Image()

        """
        self._images[image.channel][image.z_level] = image
