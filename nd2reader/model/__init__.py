import numpy as np
import skimage.io
import logging

log = logging.getLogger(__name__)


class ImageSet(object):
    """
    A group of images that share the same timestamp. NIS Elements doesn't store a unique timestamp for every
    image, rather, it stores one for each set of images that share the same field of view and z-axis level.

    """
    def __init__(self):
        self._images = []

    def add(self, image):
        """
        :type image:    nd2reader.model.Image()

        """
        self._images.append(image)

    def __iter__(self):
        for image in self._images:
            yield image


class Image(object):
    def __init__(self, timestamp, raw_array, field_of_view, channel, z_level, height, width):
        self._timestamp = timestamp
        self._raw_data = raw_array
        self._field_of_view = field_of_view
        self._channel = channel
        self._z_level = z_level
        self._height = height
        self._width = width
        self._data = None

    @property
    def field_of_view(self):
        return self._field_of_view

    @property
    def timestamp(self):
        """
        The number of seconds after the beginning of the acquisition that the image was taken. Note that for a given field
        of view and z-level offset, if you have images of multiple channels, they will all be given the same timestamp.
        No, this doesn't make much sense. But that's how ND2s are structured, so if your experiment depends on millisecond
        accuracy, you need to find an alternative imaging system.

        """
        return self._timestamp / 1000.0

    @property
    def channel(self):
        return self._channel

    @property
    def z_level(self):
        return self._z_level

    @property
    def data(self):
        if self._data is None:
            # The data is just a flat, 1-dimensional array. We convert it to a 2D image here.
            self._data = np.reshape(self._raw_data, (self._height, self._width))
        return self._data

    @property
    def is_valid(self):
        return np.any(self.data)

    def show(self):
        skimage.io.imshow(self.data)
        skimage.io.show()