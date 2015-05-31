# -*- coding: utf-8 -*-

from nd2reader.model import Image, ImageSet
from nd2reader.parser import Nd2Parser
import six


class Nd2(Nd2Parser):
    """
    Allows easy access to NIS Elements .nd2 image files.

    """
    def __init__(self, filename):
        super(Nd2, self).__init__(filename)
        self._filename = filename

    def __repr__(self):
        return "\n".join(["<ND2 %s>" % self._filename,
                          "Created: %s" % self._absolute_start.strftime("%Y-%m-%d %H:%M:%S"),
                          "Image size: %sx%s (HxW)" % (self.height, self.width),
                          "Image cycles: %s" % len(self.time_indexes),
                          "Channels: %s" % ", ".join(["'%s'" % str(channel) for channel in self.channels]),
                          "Fields of View: %s" % len(self.fields_of_view),
                          "Z-Levels: %s" % len(self.z_levels)
                          ])

    def __len__(self):
        """
        This should be the total number of images in the ND2, but it may be inaccurate. If the ND2 contains a
        different number of images in a cycle (i.e. there are "gap" images) it will be higher than reality.

        :rtype: int

        """
        return self._image_count * self._channel_count

    @property
    def height(self):
        """
        :return: height of each image, in pixels
        :rtype: int

        """
        return self.metadata[six.b('ImageAttributes')][six.b('SLxImageAttributes')][six.b('uiHeight')]

    @property
    def width(self):
        """
        :return: width of each image, in pixels
        :rtype: int

        """
        return self.metadata[six.b('ImageAttributes')][six.b('SLxImageAttributes')][six.b('uiWidth')]

    def __iter__(self):
        """
        Iterates over every image, in the order they were taken.

        :return: model.Image()

        """
        for i in range(self._image_count):
            for fov in self._fields_of_view:
                for z_level in self._z_levels:
                    for channel_name in self._channels:
                        image = self.get_image(i, fov, channel_name, z_level)
                        if image is not None:
                            yield image

    def __getitem__(self, item):
        if isinstance(item, int):
            try:
                channel_offset = item % len(self.channels)
                fov = self._calculate_field_of_view(item)
                channel = self._calculate_channel(item)
                z_level = self._calculate_z_level(item)
                item -= channel_offset
                item /= len(self.channels)
                timestamp, raw_image_data = self._get_raw_image_data(item, channel_offset)
                image = Image(timestamp, raw_image_data, fov, channel, z_level, self.height, self.width)
            except TypeError:
                return None
            else:
                return image

    def _calculate_field_of_view(self, frame_number):
        return int((frame_number - (frame_number % (len(self.z_levels) * len(self.channels)))) / (len(self.z_levels) * len(self.channels)))

    def _calculate_channel(self, frame_number):
        return self._channels[frame_number % len(self.channels)]

    def _calculate_z_level(self, frame_number):
        return self.z_levels[int(((frame_number - (frame_number % len(self.channels))) / 2) % len(self.z_levels))]

    @property
    def image_sets(self):
        """
        Iterates over groups of related images. This is useful if your ND2 contains multiple fields of view.
        A typical use case might be that you have, say, four areas of interest that you're monitoring, and every
        minute you take a bright field and GFP image of each one. For each cycle, this method would produce four
        ImageSet objects, each containing one bright field and one GFP image.

        :return: model.ImageSet()

        """
        for time_index in self._time_indexes:
            image_set = ImageSet()
            for fov in self._fields_of_view:
                for channel_name in self._channels:
                    for z_level in self._z_levels:
                        image = self.get_image(time_index, fov, channel_name, z_level)
                        if image is not None:
                            image_set.add(image)
                yield image_set

    def get_image(self, time_index, field_of_view, channel_name, z_level):
        """
        Returns an Image if data exists for the given parameters, otherwise returns None. In general, you should avoid
        using this method unless you're very familiar with the structure of ND2 files. If you have a use case that
        cannot be met by the `__iter__` or `image_sets` methods above, please create an issue on Github.

        :param time_index: the frame number
        :type time_index: int
        :param field_of_view: the label for the place in the XY-plane where this image was taken.
        :type field_of_view: int
        :param channel_name: the name of the color of this image
        :type channel_name: str
        :param z_level: the label for the location in the Z-plane where this image was taken.
        :type z_level: int
        :rtype: nd2reader.model.Image() or None

        """
        image_group_number = self._calculate_image_group_number(time_index, field_of_view, z_level)
        try:
            timestamp, raw_image_data = self._get_raw_image_data(image_group_number, self._channel_offset[channel_name])
            image = Image(timestamp, raw_image_data, field_of_view, channel_name, z_level, self.height, self.width)
        except TypeError:
            return None
        else:
            return image
