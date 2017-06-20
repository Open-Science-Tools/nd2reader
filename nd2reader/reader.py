from pims import FramesSequenceND, Frame

from nd2reader.exceptions import EmptyFileError
from nd2reader.parser import Parser
import numpy as np


class ND2Reader(FramesSequenceND):
    """PIMS wrapper for the ND2 parser.
    This is the main class: use this to process your .nd2 files.
    """

    def __init__(self, filename):
        super(self.__class__, self).__init__()
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

        # Other properties
        self._timesteps = None

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

    def _get_default(self, coord):
        try:
            return self.default_coords[coord]
        except KeyError:
            return 0

    def get_frame_2D(self, c=0, t=0, z=0, x=0, y=0):
        """Gets a given frame using the parser

        Args:
            x: The x-index (pims expects this)
            y: The y-index (pims expects this)
            c: The color channel number
            t: The frame number
            z: The z stack number

        Returns:
            numpy.ndarray: The requested frame

        """
        try:
            c_name = self.metadata["channels"][c]
        except KeyError:
            c_name = self.metadata["channels"][0]

        x = self.metadata["width"] if x <= 0 else x
        y = self.metadata["height"] if y <= 0 else y
        return self._parser.get_image_by_attributes(t, 0, c_name, z, y, x)

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

    @property
    def timesteps(self):
        """Get the timesteps of the experiment

        Returns:
            np.ndarray: an array of times in milliseconds.

        """
        if self._timesteps is None:
            return self.get_timesteps()
        return self._timesteps

    @property
    def frame_rate(self):
        """The (average) frame rate
        
        Returns:
            float: the (average) frame rate in frames per second
        """
        return 1000. / np.mean(np.diff(self.timesteps))

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
        self._init_axis_if_exists('x', self._get_metadata_property("width", default=0))
        self._init_axis_if_exists('y', self._get_metadata_property("height", default=0))
        self._init_axis_if_exists('c', len(self._get_metadata_property("channels", default=[])), min_size=2)
        self._init_axis_if_exists('t', len(self._get_metadata_property("frames", default=[])))
        self._init_axis_if_exists('z', len(self._get_metadata_property("z_levels", default=[])), min_size=2)

        if len(self.sizes) == 0:
            raise EmptyFileError("No axes were found for this .nd2 file.")

        # provide the default
        self.iter_axes = self._guess_default_iter_axis()

    def _init_axis_if_exists(self, axis, size, min_size=1):
        if size >= min_size:
            self._init_axis(axis, size)

    def _guess_default_iter_axis(self):
        """
        Guesses the default axis to iterate over based on axis sizes.
        Returns:
            the axis to iterate over
        """
        priority = ['t', 'z', 'c']
        found_axes = []
        for axis in priority:
            try:
                current_size = self.sizes[axis]
            except KeyError:
                continue

            if current_size > 1:
                return axis

            found_axes.append(axis)

        return found_axes[0]

    def get_timesteps(self):
        """Get the timesteps of the experiment

        Returns:
            np.ndarray: an array of times in milliseconds.

        """
        if self._timesteps is not None:
            return self._timesteps

        timesteps = np.array([])
        current_time = 0.0
        for loop in self.metadata['experiment']['loops']:
            if loop['stimulation']:
                continue

            if loop['sampling_interval'] == 0:
                # This is a loop were no data is acquired
                current_time += loop['duration']
                continue

            timesteps = np.concatenate(
                (timesteps, np.arange(current_time, current_time + loop['duration'], loop['sampling_interval'])))
            current_time += loop['duration']

        # if experiment did not finish, number of timesteps is wrong. Take correct amount of leading timesteps.
        self._timesteps = timesteps[:self.metadata['num_frames']]
        return self._timesteps
