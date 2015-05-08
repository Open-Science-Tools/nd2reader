# -*- coding: utf-8 -*-

from collections import namedtuple
from nd2reader.model import Channel
import logging
from nd2reader.model import Image, ImageSet
from nd2reader.reader import Nd2FileReader

chunk = namedtuple('Chunk', ['location', 'length'])
field_of_view = namedtuple('FOV', ['number', 'x', 'y', 'z', 'pfs_offset'])

print(__name__)
log = logging.getLogger(__name__)
log.setLevel(logging.WARN)


class Nd2(Nd2FileReader):
    def __init__(self, filename):
        super(Nd2, self).__init__(filename)

    def get_image(self, time_index, fov, channel_name, z_level):
        image_set_number = self._calculate_image_set_number(time_index, fov, z_level)
        timestamp, raw_image_data = self.get_raw_image_data(image_set_number, self.channel_offset[channel_name])
        return Image(timestamp, raw_image_data, fov, channel_name, z_level, self.height, self.width)

    def __iter__(self):
        """
        Just return every image in order (might not be exactly the order that the images were physically taken, but it will
        be within a few seconds). A better explanation is probably needed here.

        """
        for i in range(self._image_count):
            for fov in range(self.field_of_view_count):
                for z_level in range(self.z_level_count):
                    for channel in self.channels:
                        image = self.get_image(i, fov, channel.name, z_level)
                        if image.is_valid:
                            yield image

    def image_sets(self, field_of_view, time_indices=None, channels=None, z_levels=None):
        """
        Gets all the images for a given field of view and
        """
        timepoint_set = xrange(self.time_index_count) if time_indices is None else time_indices
        channel_set = [channel.name for channel in self.channels] if channels is None else channels
        z_level_set = xrange(self.z_level_count) if z_levels is None else z_levels

        for timepoint in timepoint_set:
            image_set = ImageSet()
            for channel_name in channel_set:
                for z_level in z_level_set:
                    image = self.get_image(timepoint, field_of_view, channel_name, z_level)
                    if image.is_valid:
                        image_set.add(image)
            yield image_set

        self._channel_offset = None

    @property
    def height(self):
        """
        :return:    height of each image, in pixels

        """
        return self._metadata['ImageAttributes']['SLxImageAttributes']['uiHeight']

    @property
    def width(self):
        """
        :return:    width of each image, in pixels

        """
        return self._metadata['ImageAttributes']['SLxImageAttributes']['uiWidth']

    @property
    def channels(self):
        metadata = self._metadata['ImageMetadataSeq']['SLxPictureMetadata']['sPicturePlanes']
        try:
            validity = self._metadata['ImageMetadata']['SLxExperiment']['ppNextLevelEx'][''][0]['ppNextLevelEx'][''][0]['pItemValid']
        except KeyError:
            # If none of the channels have been deleted, there is no validity list, so we just make one
            validity = [True for i in metadata]
        # Channel information is contained in dictionaries with the keys a0, a1...an where the number
        # indicates the order in which the channel is stored. So by sorting the dicts alphabetically
        # we get the correct order.
        for (label, chan), valid in zip(sorted(metadata['sPlaneNew'].items()), validity):
            if not valid:
                continue
            name = chan['sDescription']
            exposure_time = metadata['sSampleSetting'][label]['dExposureTime']
            camera = metadata['sSampleSetting'][label]['pCameraSetting']['CameraUserName']
            yield Channel(name, camera, exposure_time)

    @property
    def channel_names(self):
        """
        A convenience method for getting an alphabetized list of channel names.

        :return:    list[str]

        """
        for channel in sorted(self.channels, key=lambda x: x.name):
            yield channel.name

    @property
    def _image_count(self):
        return self._metadata['ImageAttributes']['SLxImageAttributes']['uiSequenceCount']

    @property
    def _sequence_count(self):
        return self._metadata['ImageEvents']['RLxExperimentRecord']['uiCount']

    @property
    def channel_offset(self):
        if self._channel_offset is None:
            self._channel_offset = {}
            for n, channel in enumerate(self.channels):
                self._channel_offset[channel.name] = n
        return self._channel_offset

    def _calculate_image_set_number(self, time_index, fov, z_level):
        return time_index * self.field_of_view_count * self.z_level_count + (fov * self.z_level_count + z_level)


