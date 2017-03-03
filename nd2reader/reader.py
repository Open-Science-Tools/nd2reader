from pims import FramesSequenceND, Frame
from nd2reader.parser import Parser
import numpy as np


class ND2Reader(FramesSequenceND):
    """
    PIMS wrapper for the ND2 parser
    """

    def __init__(self, filename):
        self.filename = filename

        # first use the parser to parse the file
        self._fh = open(filename, "rb")
        self._parser = Parser(self._fh)

        # Setup metadata
        self.metadata = self._parser.metadata

        # Set data type
        self._dtype = self._parser.get_dtype_from_metadata()

        # Setup the axes
        self._setup_axes()

    @classmethod
    def class_exts(cls):
        """
        So PIMS open function can use this reader for opening .nd2 files
        :return:
        """
        return {'nd2'} | super(ND2Reader, cls).class_exts()

    def close(self):
        """
        Correctly close the file handle
        :return:
        """
        if self._fh is not None:
            self._fh.close()

    def get_frame(self, i):
        """
        Return one frame
        :param i:
        :return:
        """
        fetch_all_channels = 'c' in self.bundle_axes

        if fetch_all_channels:
            return self._get_frame_all_channels(i)
        else:
            return self.get_frame_2D(self.default_coords['c'], i, self.default_coords['z'])

    def _get_frame_all_channels(self, i):
        """
        Get all color channels for this frame
        :return:
        """
        frames = None
        for c in range(len(self.metadata["channels"])):
            frame = self.get_frame_2D(c, i, self.default_coords['z'])
            if frames is None:
                frames = Frame([frame])
            else:
                frames = np.concatenate((frames, [frame]), axis=0)
        return frames

    def get_frame_2D(self, c, t, z):
        """
        Gets a given frame using the parser
        :param c:
        :param t:
        :param z:
        :return:
        """
        c_name = self.metadata["channels"][c]
        return self._parser.get_image_by_attributes(t, 0, c_name, z, self.metadata["height"], self.metadata["width"])

    @property
    def pixel_type(self):
        """
        Return the pixel data type
        :return:
        """
        return self._dtype

    def _setup_axes(self):
        """
        Setup the xyctz axes, iterate over t axis by default
        :return:
        """
        self._init_axis('x', self.metadata["width"])
        self._init_axis('y', self.metadata["height"])
        self._init_axis('c', len(self.metadata["channels"]))
        self._init_axis('t', len(self.metadata["frames"]))
        self._init_axis('z', len(self.metadata["z_levels"]))

        # provide the default
        self.iter_axes = 't'
