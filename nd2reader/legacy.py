"""
Legacy class for backwards compatibility
"""

import warnings

from nd2reader import ND2Reader


class Nd2(object):
    """ Warning: this module is deprecated and only maintained for backwards compatibility with the non-PIMS version of
    nd2reader.
    """

    def __init__(self, filename):
        warnings.warn(
            "The 'Nd2' class is deprecated, please consider using the new ND2Reader interface which uses pims.",
            DeprecationWarning)

        self.reader = ND2Reader(filename)

    def __repr__(self):
        return "\n".join(["<Deprecated ND2 %s>" % self.reader.filename,
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
        if self.reader is not None:
            self.reader.close()

    def __len__(self):
        return len(self.reader)

    def __getitem__(self, item):
        return self.reader[item]

    def select(self, fields_of_view=None, channels=None, z_levels=None, start=0, stop=None):
        """Select images based on criteria.

        Args:
            fields_of_view: the fields of view
            channels: the color channels
            z_levels: the z levels
            start: the starting frame
            stop: the last frame

        Returns:
            ND2Reader: Sliced ND2Reader which contains the frames

        """
        if stop is None:
            stop = len(self.frames)

        return self.reader[start:stop]

    def get_image(self, frame_number, field_of_view, channel_name, z_level):
        """Deprecated. Returns the specified image from the ND2Reader class.

        Args:
            frame_number: the frame number
            field_of_view: the field of view number
            channel_name: the name of the color channel
            z_level: the z level number

        Returns:
            Frame: the specified image

        """
        return self.reader.parser.get_image_by_attributes(frame_number, field_of_view, channel_name, z_level,
                                                          self.height, self.width)

    def close(self):
        """Closes the ND2Reader
        """
        if self.reader is not None:
            self.reader.close()

    @property
    def height(self):
        """Deprecated. Fetches the height of the image.

        Returns:
            int: the pixel height of the image

        """
        return self._get_width_or_height("height")

    @property
    def width(self):
        """Deprecated. Fetches the width of the image.

        Returns:
            int: the pixel width of the image

        """
        return self._get_width_or_height("width")

    def _get_width_or_height(self, key):
        return self.reader.metadata[key] if self.reader.metadata[key] is not None else 0

    @property
    def z_levels(self):
        """Deprecated. Fetches the available z levels.

        Returns:
            list: z levels.

        """
        return self.reader.metadata["z_levels"]

    @property
    def fields_of_view(self):
        """Deprecated. Fetches the fields of view.

        Returns:
            list: fields of view.

        """
        return self.reader.metadata["fields_of_view"]

    @property
    def channels(self):
        """Deprecated. Fetches all color channels.

        Returns:
            list: the color channels.

        """
        return self.reader.metadata["channels"]

    @property
    def frames(self):
        """Deprecated. Fetches all frames.

        Returns:
            list: list of frames

        """
        return self.reader.metadata["frames"]

    @property
    def date(self):
        """Deprecated. Fetches the acquisition date.

        Returns:
            string: the date

        """
        return self.reader.metadata["date"]

    @property
    def pixel_microns(self):
        """Deprecated. Fetches the amount of microns per pixel.

        Returns:
            float: microns per pixel

        """
        return self.reader.metadata["pixel_microns"]
