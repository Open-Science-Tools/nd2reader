# -*- coding: utf-8 -*-

from nd2reader.parser import get_parser
from nd2reader.version import get_version
import warnings


class Nd2(object):
    """
    Allows easy access to NIS Elements .nd2 image files.

    """
    def __init__(self, filename):
        self._filename = filename
        self._fh = open(filename, "rb")
        major_version, minor_version = get_version(self._fh)
        parser = get_parser(self._fh, major_version, minor_version)
        self._driver = parser.driver
        self._metadata = parser.metadata

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._fh is not None:
            self._fh.close()
        
    def __repr__(self):
        return "\n".join(["<ND2 %s>" % self._filename,
                          "Created: %s" % (self.date if self.date is not None else "Unknown"),
                          "Image size: %sx%s (HxW)" % (self.height, self.width),
                          "Frames: %s" % len(self.frames),
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
        return self._metadata.total_images_per_channel * len(self.channels)

    def __getitem__(self, item):
        """
        Allows slicing ND2s.

        :type item: int or slice
        :rtype: nd2reader.model.Image() or generator

        """
        if isinstance(item, int):
            try:
                image = self._driver.get_image(item)
            except KeyError:
                raise IndexError
            else:
                return image
        elif isinstance(item, slice):
            return self._slice(item.start, item.stop, item.step)
        raise IndexError

    def _slice(self, start, stop, step):
        """
        Allows for iteration over a selection of the entire dataset.

        :type start: int
        :type stop: int
        :type step: int
        :rtype: nd2reader.model.Image()

        """
        start = start if start is not None else 0
        step = step if step is not None else 1
        stop = stop if stop is not None else len(self)
        # This weird thing with the step allows you to iterate backwards over the images
        for i in range(start, stop)[::step]:
            yield self[i]

    @property
    def date(self):
        return self._metadata.date

    @property
    def z_levels(self):
        return self._metadata.z_levels

    @property
    def fields_of_view(self):
        return self._metadata.fields_of_view

    @property
    def channels(self):
        return self._metadata.channels

    @property
    def frames(self):
        return self._metadata.frames

    @property
    def height(self):
        """
        :return: height of each image, in pixels
        :rtype: int

        """
        return self._metadata.height

    @property
    def width(self):
        """
        :return: width of each image, in pixels
        :rtype: int

        """
        return self._metadata.width

    def get_image(self, frame_number, field_of_view, channel_name, z_level):
        """
        Returns an Image if data exists for the given parameters, otherwise returns None.

        :type frame_number: int
        :param field_of_view: the label for the place in the XY-plane where this image was taken.
        :type field_of_view: int
        :param channel_name: the name of the color of this image
        :type channel_name: str
        :param z_level: the label for the location in the Z-plane where this image was taken.
        :type z_level: int

        :rtype: nd2reader.model.Image()

        """
        return self._driver.get_image_by_attributes(frame_number, field_of_view, channel_name, z_level, self.height, self.width)

    def close(self):
        self._fh.close()
