# -*- coding: utf-8 -*-

import logging
from nd2reader.model import Image, ImageSet
from nd2reader.parser import Nd2Parser


log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.WARNING)


class Nd2(Nd2Parser):
    def __init__(self, filename):
        super(Nd2, self).__init__(filename)
        self._filename = filename

    def __repr__(self):
        return "\n".join(["ND2: %s" % self._filename,
                          "Created: %s" % self._absolute_start.strftime("%Y-%m-%d %H:%M:%S"),
                          "Image size: %sx%s (HxW)" % (self.height, self.width),
                          "Image cycles: %s" % self._time_index_count,
                          "Channels: %s" % ", ".join(["'%s'" % channel for channel in self._channels]),
                          "Fields of View: %s" % self._field_of_view_count,
                          "Z-Levels: %s" % self._z_level_count
                          ])

    def __iter__(self):
        for i in range(self._image_count):
            for fov in range(self._field_of_view_count):
                for z_level in range(self._z_level_count):
                    for channel_name in self._channels:
                        image = self.get_image(i, fov, channel_name, z_level)
                        if image is not None:
                            yield image

    @property
    def image_sets(self):
        for time_index in xrange(self._time_index_count):
            image_set = ImageSet()
            for fov in range(self._field_of_view_count):
                for channel_name in self._channels:
                    for z_level in xrange(self._z_level_count):
                        image = self.get_image(time_index, fov, channel_name, z_level)
                        if image is not None:
                            image_set.add(image)
                yield image_set

    def get_image(self, time_index, fov, channel_name, z_level):
        image_set_number = self._calculate_image_set_number(time_index, fov, z_level)
        try:
            timestamp, raw_image_data = self._get_raw_image_data(image_set_number, self._channel_offset[channel_name])
            image = Image(timestamp, raw_image_data, fov, channel_name, z_level, self.height, self.width)
        except TypeError:
            return None
        else:
            return image

    @property
    def height(self):
        """
        :return:    height of each image, in pixels

        """
        return self.metadata['ImageAttributes']['SLxImageAttributes']['uiHeight']

    @property
    def width(self):
        """
        :return:    width of each image, in pixels

        """
        return self.metadata['ImageAttributes']['SLxImageAttributes']['uiWidth']
