# -*- coding: utf-8 -*-

from nd2reader.parser import get_parser
from nd2reader.version import get_version
import six


class Nd2(object):
    """ Allows easy access to NIS Elements .nd2 image files. """

    def __init__(self, filename):
        self._filename = filename
        self._fh = open(filename, "rb")
        major_version, minor_version = get_version(self._fh)
        self._parser = get_parser(self._fh, major_version, minor_version)
        self._metadata = self._parser.metadata
        
    def __repr__(self):
        return "\n".join(["<ND2 %s>" % self._filename,
                          "Created: %s" % (self.date if self.date is not None else "Unknown"),
                          "Image size: %sx%s (HxW)" % (self.height, self.width),
                          "Frames: %s" % len(self.frames),
                          "Channels: %s" % ", ".join(["%s" % str(channel) for channel in self.channels]),
                          "Fields of View: %s" % len(self.fields_of_view),
                          "Z-Levels: %s" % len(self.z_levels)
                          ])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._fh is not None:
            self._fh.close()

    def __len__(self):
        """
        This should be the total number of images in the ND2, but it may be inaccurate. If the ND2 contains a
        different number of images in a cycle (i.e. there are "gap" images) it will be higher than reality.

        :rtype:    int

        """
        return self._metadata.total_images_per_channel * len(self.channels)

    def __getitem__(self, item):
        """
        Allows slicing ND2s.

        :type item:    int or slice
        :rtype:    nd2reader.model.Image() or generator

        """
        if isinstance(item, int):
            try:
                image = self._parser.driver.get_image(item)
            except KeyError:
                raise IndexError
            else:
                return image
        elif isinstance(item, slice):
            return self._slice(item.start, item.stop, item.step)
        raise IndexError

    def select(self, fields_of_view=None, channels=None, z_levels=None):
        """
        Iterates over images matching the given criteria. This can be 2-10 times faster than manually iterating over
        the Nd2 and checking the attributes of each image, as this method skips disk reads for any images that don't
        meet the criteria.

        :type fields_of_view:   int or tuple or list
        :type channels:     str or tuple or list
        :type z_levels:     int or tuple or list

        """
        fields_of_view = self._to_list(fields_of_view, self.fields_of_view)
        channels = self._to_list(channels, self.channels)
        z_levels = self._to_list(z_levels, self.z_levels)

        for frame in self.frames:
            field_of_view, channel, z_level = self._parser.driver.calculate_image_properties(frame)
            if field_of_view in fields_of_view and channel in channels and z_level in z_levels:
                image = self._parser.driver.get_image(frame)
                if image is not None:
                    yield image

    @property
    def height(self):
        """
        The height of each image in pixels.

        :rtype:    int

        """
        return self._metadata.height

    @property
    def width(self):
        """
        The width of each image in pixels.

        :rtype:    int

        """
        return self._metadata.width

    @property
    def z_levels(self):
        """
        A list of integers that represent the different levels on the Z-axis that images were taken. Currently this is
        just a list of numbers from 0 to N. For example, an ND2 where images were taken at -3µm, 0µm, and +5µm from a
        set position would be represented by 0, 1 and 2, respectively. ND2s do store the actual offset of each image
        in micrometers and in the future this will hopefully be available. For now, however, you will have to match up
        the order yourself.

        :return:    list of int

        """
        return self._metadata.z_levels

    @property
    def fields_of_view(self):
        """
        A list of integers representing the various stage locations, in the order they were taken in the first round
        of acquisition.

        :return:    list of int

        """
        return self._metadata.fields_of_view

    @property
    def channels(self):
        """
        A list of channel (i.e. wavelength) names. These are set by the user in NIS Elements.

        :return:    list of str

        """
        return self._metadata.channels

    @property
    def frames(self):
        """
        A list of integers representing groups of images. ND2s consider images to be part of the same frame if they
        are in the same field of view and don't have the same channel. So if you take a bright field and GFP image at
        four different fields of view over and over again, you'll have 8 images and 4 frames per cycle.

        :return:    list of int

        """
        return self._metadata.frames

    @property
    def camera_settings(self):
        return self._parser.camera_metadata
    
    @property
    def date(self):
        """
        The date and time that the acquisition began. Not guaranteed to have been recorded.

        :rtype:    datetime.datetime() or None

        """
        return self._metadata.date

    def get_image(self, frame_number, field_of_view, channel_name, z_level):
        """
        Attempts to return the image with the unique combination of given attributes. None will be returned if a match
        is not found.

        :type frame_number:    int
        :param field_of_view:    the label for the place in the XY-plane where this image was taken.
        :type field_of_view:    int
        :param channel_name:    the name of the color of this image
        :type channel_name:    str
        :param z_level:    the label for the location in the Z-plane where this image was taken.
        :type z_level:    int

        :rtype: nd2reader.model.Image() or None

        """
        return self._parser.driver.get_image_by_attributes(frame_number,
                                                           field_of_view,
                                                           channel_name,
                                                           z_level,
                                                           self.height,
                                                           self.width)

    def _slice(self, start, stop, step):
        """
        Allows for iteration over a selection of the entire dataset.

        :type start:    int
        :type stop:    int
        :type step:    int
        :rtype:    nd2reader.model.Image()

        """
        start = start if start is not None else 0
        step = step if step is not None else 1
        stop = stop if stop is not None else len(self)
        # This weird thing with the step allows you to iterate backwards over the images
        for i in range(start, stop)[::step]:
            yield self[i]

    def _to_list(self, value, default):
        """
        Idempotently converts a value to a tuple. This allows users to pass in scalar values and iterables to
        select(), which is more ergonomic than having to remember to pass in single-member lists

        :type value:    int or str or tuple or list
        :type default:  tuple or list
        :rtype:     tuple

        """
        value = default if value is None else value
        return (value,) if isinstance(value, int) or isinstance(value, six.string_types) else tuple(value)

    def close(self):
        """
        Closes the file handle to the image. This actually sometimes will prevent problems so it's good to do this or
        use Nd2 as a context manager.

        """
        self._fh.close()
