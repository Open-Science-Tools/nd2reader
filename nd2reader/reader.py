from pims import FramesSequenceND, Frame
from nd2reader.parser import Parser
import numpy as np


class ND2Reader(FramesSequenceND):
    """PIMS wrapper for the ND2 parser

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
        """Let PIMS open function use this reader for opening .nd2 files

        """
        return {'nd2'} | super(ND2Reader, cls).class_exts()

    def close(self):
        """Correctly close the file handle

        """
        if self._fh is not None:
            self._fh.close()

    def get_frame(self, i):
        """Return one frame

        Args:
            i: The frame number

        Returns:
            numpy.ndarray: The requested frame

        """
        fetch_all_channels = 'c' in self.bundle_axes

        if fetch_all_channels:
            return self._get_frame_all_channels(i)
        else:
            return self.get_frame_2D(self.default_coords['c'], i, self.default_coords['z'])

    def _get_frame_all_channels(self, i):
        """Get all color channels for this frame

        Args:
            i: The frame number

        Returns:
            numpy.ndarray: The requested frame, with all color channels.

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
        """Gets a given frame using the parser

        Args:
            c: The color channel number
            t: The frame number
            z: The z stack number

        Returns:
            numpy.ndarray: The requested frame

        """
        c_name = self.metadata["channels"][c]
        return self._parser.get_image_by_attributes(t, 0, c_name, z, self.metadata["height"], self.metadata["width"])

    @property
    def parser(self):
        """
        Returns the parser object.
        Returns:
            Parser: the parser object
        """
        return self._parser

    @property
    def pixel_type(self):
        """Return the pixel data type

        Returns:
            dtype: the pixel data type

        """
        return self._dtype

    def _get_metadata_property(self, key, default=None):
        if self.metadata is None:
            return default

        if key not in self.metadata:
            return default

        if self.metadata[key] is None:
            return default

        return self.metadata[key]

    def _setup_axes(self):
        """Setup the xyctz axes, iterate over t axis by default

        """
        self._init_axis('x', self._get_metadata_property("width", default=0))
        self._init_axis('y', self._get_metadata_property("height", default=0))
        self._init_axis('c', len(self._get_metadata_property("channels", default=[])))
        self._init_axis('t', len(self._get_metadata_property("frames", default=[])))
        self._init_axis('z', len(self._get_metadata_property("z_levels", default=[])))

        # provide the default
        self.iter_axes = 't'

    def get_timesteps(self):
        """Get the timesteps of the experiment

        Returns:
            np.ndarray: an array of times in milliseconds.

        """
        timesteps = np.array([])
        current_time = 0.0
        for loop in self.metadata['experiment']['loops']:
            if loop['stimulation']:
                continue

            timesteps = np.concatenate(
                (timesteps, np.arange(current_time, current_time + loop['duration'], loop['sampling_interval'])))
            current_time += loop['duration']

        # if experiment did not finish, number of timesteps is wrong. Take correct amount of leading timesteps.
        return timesteps[:self.metadata['num_frames']]
