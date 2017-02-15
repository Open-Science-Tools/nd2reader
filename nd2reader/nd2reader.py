from pims import FramesSequenceND, Frame
import numpy as np

from nd2reader.exc import NoImageError
from nd2reader.parser import get_parser
from nd2reader.version import get_version
import six


class ND2Reader(FramesSequenceND):
    """
    PIMS wrapper for the ND2 reader
    """

    def __init__(self, filename):
        self.filename = filename

        # first use the parser to parse the file
        self._fh = open(filename, "rb")
        major_version, minor_version = get_version(self._fh)
        self._parser = get_parser(self._fh, major_version, minor_version)
        self._metadata = self._parser.metadata
        self._roi_metadata = self._parser.roi_metadata

        # Set data type
        bit_depth = self._parser.raw_metadata.image_attributes[six.b('SLxImageAttributes')][six.b('uiBpcInMemory')]
        if bit_depth <= 16:
            self._dtype = np.float16
        elif bit_depth <= 32:
            self._dtype = np.float32
        else:
            self._dtype = np.float64

        # Setup the axes
        self._init_axis('x', self._metadata.width)
        self._init_axis('y', self._metadata.height)
        self._init_axis('c', len(self._metadata.channels))
        self._init_axis('t', len(self._metadata.frames))
        self._init_axis('z', len(self._metadata.z_levels))

    def close(self):
        if self._fh is not None:
            self._fh.close()

    def get_frame_2D(self, c, t, z):
        """
        Gets a given frame using the parser
        :param c:
        :param t:
        :param z:
        :return:
        """
        c_name = self._metadata.channels[c]
        try:
            image = self._parser.driver.get_image_by_attributes(t, 0, c_name, z, self._metadata.width,
                                                                self._metadata.height)
        except (TypeError, NoImageError):
            return Frame([])
        else:
            return Frame(image, frame_no=image.frame_number)

    @property
    def pixel_type(self):
        return self._dtype
