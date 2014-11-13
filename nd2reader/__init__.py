import logging
from nd2reader.service import BaseNd2
from nd2reader.model import Image

log = logging.getLogger("nd2reader")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)


class Nd2(BaseNd2):
    def __init__(self, filename):
        super(Nd2, self).__init__(filename)

    def get_image(self, timepoint, fov, channel_name, z_level):
        image_set_number = self._calculate_image_set_number(timepoint, fov, z_level)
        timestamp, raw_image_data = self._reader.get_raw_image_data(image_set_number, self.channel_offset[channel_name])
        return Image(timestamp, raw_image_data, self.height, self.width)

    def __iter__(self):
        """
        Just return every image.

        """
        for i in range(self._image_count):
            for fov in range(self._field_of_view_count):
                for z_level in range(self._z_level_count):
                    for channel in self.channels:
                        image = self.get_image(i, fov, channel.name, z_level)
                        if image.is_valid:
                            yield image