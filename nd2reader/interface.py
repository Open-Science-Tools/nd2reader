# -*- coding: utf-8 -*-

from nd2reader.model import ImageGroup
from nd2reader.driver import get_driver
from nd2reader.driver.version import get_version
import warnings


class Nd2(object):
    """
    Allows easy access to NIS Elements .nd2 image files.

    """
    def __init__(self, filename):
        self._filename = filename
        version = get_version(filename)
        self._driver = get_driver(filename, version)
        self._metadata = self._driver.get_metadata()
        
    def __repr__(self):
        return "\n".join(["<ND2 %s>" % self._filename,
                          "Created: %s" % self.date,
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
        return self._driver.total_images_per_channel * len(self.channels)

    def __getitem__(self, item):
        """
        Allows slicing ND2s.

        >>> nd2 = Nd2("my_images.nd2")
        >>> image = nd2[16]  # gets 17th frame
        >>> for image in nd2[100:200]:  # iterate over the 100th to 200th images
        >>>     do_something(image)
        >>> for image in nd2[::-1]:  # iterate backwards
        >>>     do_something(image)
        >>> for image in nd2[37:422:17]:  # do something super weird if you really want to
        >>>     do_something(image)

        :type item: int or slice
        :rtype: nd2reader.model.Image() or generator

        """
        if isinstance(item, int):
            return self._driver.get_image(item)
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
    def image_sets(self):
        """
        Iterates over groups of related images. This is useful if your ND2 contains multiple fields of view.
        A typical use case might be that you have, say, four areas of interest that you're monitoring, and every
        minute you take a bright field and GFP image of each one. For each cycle, this method would produce four
        ImageSet objects, each containing one bright field and one GFP image.

        :return: model.ImageSet()

        """
        warnings.warn("nd2.image_sets will be removed from the nd2reader library in the near future.", DeprecationWarning)

        for frame in self.frames:
            image_group = ImageGroup()
            for fov in self.fields_of_view:
                for channel_name in self.channels:
                    for z_level in self.z_levels:
                        image = self.get_image(frame, fov, channel_name, z_level)
                        if image is not None:
                            image_group.add(image)
                yield image_group

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
        return self._driver.get_image_by_attributes(frame_number, field_of_view, channel_name, z_level)
