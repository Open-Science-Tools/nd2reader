from pims import FramesSequenceND, Frame
import numpy as np

from nd2reader.exc import NoImageError
from nd2reader.parser import get_parser
import six


class ND2Reader(FramesSequenceND):
    """
    PIMS wrapper for the ND2 reader
    """

    def __init__(self, filename):
        self.filename = filename

        # first use the parser to parse the file
        self._fh = open(filename, "rb")
        self._parser = get_parser(self._fh)
        self._metadata = self._parser.metadata
        self._roi_metadata = self._parser.roi_metadata

        # Set data type
        self._dtype = self._get_dtype_from_metadata()

        # Setup the axes
        self._init_axis('x', self._metadata.width)
        self._init_axis('y', self._metadata.height)
        self._init_axis('c', len(self._metadata.channels))
        self._init_axis('t', len(self._metadata.frames))
        self._init_axis('z', len(self._metadata.z_levels))

        # provide the default
        self.iter_axes = 't'

    def _get_dtype_from_metadata(self):
        """
        Determine the data type from the metadata.
        :return:
        """
        bit_depth = self._parser.raw_metadata.image_attributes[six.b('SLxImageAttributes')][six.b('uiBpcInMemory')]
        if bit_depth <= 16:
            self._dtype = np.float16
        elif bit_depth <= 32:
            self._dtype = np.float32
        else:
            self._dtype = np.float64

        return self._dtype

    @classmethod
    def class_exts(cls):
        return {'nd2'} | super(ND2Reader, cls).class_exts()

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
            return Frame(image, frame_no=image.frame_number, metadata=self._get_frame_metadata())

    def _get_frame_metadata(self):
        """
        Get the metadata for one frame
        :return:
        """
        frame_metadata = {
            "height": self._metadata.height,
            "width": self._metadata.width,
            "date": self._metadata.date,
            "pixel_microns": self._metadata.pixel_microns,
            "rois": self._roi_metadata
        }

        return frame_metadata

    @property
    def pixel_type(self):
        return self._dtype
