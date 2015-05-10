# -*- coding: utf-8 -*-

from nd2reader.model import Channel
from datetime import datetime
import logging
from nd2reader.model import Image, ImageSet
from nd2reader.reader import Nd2FileReader


log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.WARN)


class Nd2(Nd2FileReader):
    def __init__(self, filename):
        super(Nd2, self).__init__(filename)

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
    def metadata(self):
        return self._metadata

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
    def absolute_start(self):
        if self._absolute_start is None:
            for line in self._metadata['ImageTextInfo']['SLxImageTextInfo'].values():
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
                self._absolute_start = absolute_start_12 if absolute_start_12 else absolute_start_24
        return self._absolute_start