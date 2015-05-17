# -*- coding: utf-8 -*-

import array
from datetime import datetime
import logging
from nd2reader.model import Image, ImageSet
from nd2reader.parser import Nd2Parser
import re
import struct

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.WARNING)


class Nd2(Nd2Parser):
    def __init__(self, filename):
        super(Nd2, self).__init__(filename)
        self._filename = filename

    def __repr__(self):
        return "\n".join(["ND2: %s" % self._filename,
                          "Created: %s" % self.absolute_start.strftime("%Y-%m-%d %H:%M:%S"),
                          "Image size: %sx%s (HxW)" % (self.height, self.width),
                          "Image cycles: %s" % self.time_index_count,
                          "Channels: %s" % ", ".join(["'%s'" % channel for channel in self.channels]),
                          "Fields of View: %s" % self.field_of_view_count,
                          "Z-Levels: %s" % self.z_level_count
                          ])

    def __iter__(self):
        for i in range(self._image_count):
            for fov in range(self.field_of_view_count):
                for z_level in range(self.z_level_count):
                    for channel_name in self.channels:
                        image = self.get_image(i, fov, channel_name, z_level)
                        if image is not None:
                            yield image

    @property
    def image_sets(self):
        for time_index in xrange(self.time_index_count):
            image_set = ImageSet()
            for fov in range(self.field_of_view_count):
                for channel_name in self.channels:
                    for z_level in xrange(self.z_level_count):
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
    def channels(self):
        metadata = self.metadata['ImageMetadataSeq']['SLxPictureMetadata']['sPicturePlanes']
        try:
            validity = self.metadata['ImageMetadata']['SLxExperiment']['ppNextLevelEx'][''][0]['ppNextLevelEx'][''][0]['pItemValid']
        except KeyError:
            # If none of the channels have been deleted, there is no validity list, so we just make one
            validity = [True for _ in metadata]
        # Channel information is contained in dictionaries with the keys a0, a1...an where the number
        # indicates the order in which the channel is stored. So by sorting the dicts alphabetically
        # we get the correct order.
        for (label, chan), valid in zip(sorted(metadata['sPlaneNew'].items()), validity):
            if not valid:
                continue
            yield chan['sDescription']

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

    @property
    def absolute_start(self):
        for line in self.metadata['ImageTextInfo']['SLxImageTextInfo'].values():
            absolute_start_12 = None
            absolute_start_24 = None
            # ND2s seem to randomly switch between 12- and 24-hour representations.
            try:
                absolute_start_24 = datetime.strptime(line, "%m/%d/%Y  %H:%M:%S")
            except ValueError:
                pass
            try:
                absolute_start_12 = datetime.strptime(line, "%m/%d/%Y  %I:%M:%S %p")
            except ValueError:
                pass
            if not absolute_start_12 and not absolute_start_24:
                continue
            return absolute_start_12 if absolute_start_12 else absolute_start_24
        raise ValueError("This ND2 has no recorded start time. This is probably a bug.")

    @property
    def channel_count(self):
        pattern = r""".*?λ\((\d+)\).*?"""
        try:
            count = int(re.match(pattern, self._dimensions).group(1))
        except AttributeError:
            return 1
        else:
            return count

    @property
    def field_of_view_count(self):
        """
        The metadata contains information about fields of view, but it contains it even if some fields
        of view were cropped. We can't find anything that states which fields of view are actually
        in the image data, so we have to calculate it. There probably is something somewhere, since
        NIS Elements can figure it out, but we haven't found it yet.

        """
        pattern = r""".*?XY\((\d+)\).*?"""
        try:
            count = int(re.match(pattern, self._dimensions).group(1))
        except AttributeError:
            return 1
        else:
            return count

    @property
    def time_index_count(self):
        """
        The number of cycles.

        :rtype:     int

        """
        pattern = r""".*?T'\((\d+)\).*?"""
        try:
            count = int(re.match(pattern, self._dimensions).group(1))
        except AttributeError:
            return 1
        else:
            return count

    @property
    def z_level_count(self):
        pattern = r""".*?Z\((\d+)\).*?"""
        try:
            count = int(re.match(pattern, self._dimensions).group(1))
        except AttributeError:
            return 1
        else:
            return count

    @property
    def _channel_offset(self):
        """
        Image data is interleaved for each image set. That is, if there are four images in a set, the first image
        will consist of pixels 1, 5, 9, etc, the second will be pixels 2, 6, 10, and so forth. Why this would be the
        case is beyond me, but that's how it works.

        """
        channel_offset = {}
        for n, channel in enumerate(self.channels):
            channel_offset[channel] = n
        return channel_offset

    def _get_raw_image_data(self, image_set_number, channel_offset):
        chunk = self._label_map["ImageDataSeq|%d!" % image_set_number]
        data = self._read_chunk(chunk)
        timestamp = struct.unpack("d", data[:8])[0]
        # The images for the various channels are interleaved within each other.
        image_data = array.array("H", data)
        image_data_start = 4 + channel_offset
        if any(image_data):
            return timestamp, image_data[image_data_start::self.channel_count]
        return None

    def _calculate_image_set_number(self, time_index, fov, z_level):
        return time_index * self.field_of_view_count * self.z_level_count + (fov * self.z_level_count + z_level)