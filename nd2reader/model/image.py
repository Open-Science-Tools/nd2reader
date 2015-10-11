# -*- coding: utf-8 -*-

import numpy as np
import warnings


class Image(np.ndarray):
    def __new__(cls, array):
        return np.asarray(array).view(cls)

    def __init__(self, array):
        self._timestamp = None
        self._frame_number = None
        self._field_of_view = None
        self._channel = None
        self._z_level = None

    def add_params(self, timestamp, frame_number, field_of_view, channel, z_level):
        """
        A wrapper around the raw pixel data of an image.

        :param timestamp: The number of milliseconds after the beginning of the acquisition that this image was taken.
        :type timestamp: float
        :param frame_number:    The order in which this image was taken, with images of different channels/z-levels
                                at the same field of view treated as being in the same frame.
        :type frame_number:     int
        :param field_of_view: The label for the place in the XY-plane where this image was taken.
        :type field_of_view: int
        :param channel: The name of the color of this image
        :type channel: str
        :param z_level: The label for the location in the Z-plane where this image was taken.
        :type z_level: int

        """
        self._timestamp = timestamp
        self._frame_number = int(frame_number)
        self._field_of_view = field_of_view
        self._channel = channel
        self._z_level = z_level

    @property
    def height(self):
        return self.shape[1]

    @property
    def width(self):
        return self.shape[0]

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

    @property
    def data(self):
        warnings.warn("Image objects now directly subclass Numpy arrays, so using the data attribute will be removed in the near future.", DeprecationWarning)
        return self
