import numpy as np
import skimage.io


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
    def __init__(self, timestamp, raw_array, height, width):
        self._timestamp = timestamp
        self._raw_data = raw_array
        self._data = np.reshape(self._raw_data, (height, width))

    @property
    def timestamp(self):
        # TODO: Convert to datetime object
        return self._timestamp

    @property
    def data(self):
        return self._data

    @property
    def is_valid(self):
        return np.any(self._data)

    def show(self):
        skimage.io.imshow(self.data)
        skimage.io.show()