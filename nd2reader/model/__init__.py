import numpy as np
import skimage.io
import logging

log = logging.getLogger("nd2reader")


class Channel(object):
    def __init__(self, name, camera, exposure_time):
        self._name = name
        self._camera = camera
        self._exposure_time = exposure_time

    @property
    def name(self):
        return self._name

    @property
    def camera(self):
        return self._camera

    @property
    def exposure_time(self):
        return self._exposure_time


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
    def timestamp(self):
        # TODO: Convert to datetime object
        return self._timestamp / 1000.0

    @property
    def data(self):
        if self._data is None:
            self._data = np.reshape(self._raw_data, (self._height, self._width))
        return self._data

    @property
    def is_valid(self):
        return np.any(self.data)

    def show(self):
        skimage.io.imshow(self.data)
        skimage.io.show()