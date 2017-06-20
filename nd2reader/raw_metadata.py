import re
from nd2reader.common import read_chunk, read_array, read_metadata, parse_date, get_from_dict_if_exists
import xmltodict
import six
import numpy as np


class RawMetadata(object):
    """RawMetadata class parses and stores the raw metadata that is read from the binary file in dict format.
    """

    def __init__(self, fh, label_map):
        self._fh = fh
        self._label_map = label_map
        self._metadata_parsed = None

    @property
    def __dict__(self):
        """Returns the parsed metadata in dictionary form.

        Returns:
            dict: the parsed metadata
        """
        return self.get_parsed_metadata()

    def get_parsed_metadata(self):
        """Returns the parsed metadata in dictionary form.

        Returns:
            dict: the parsed metadata
        """

        if self._metadata_parsed is not None:
            return self._metadata_parsed

        frames_per_channel = self._parse_total_images_per_channel()
        self._metadata_parsed = {
            "height": self._parse_if_not_none(self.image_attributes, self._parse_height),
            "width": self._parse_if_not_none(self.image_attributes, self._parse_width),
            "date": self._parse_if_not_none(self.image_text_info, self._parse_date),
            "fields_of_view": self._parse_fields_of_view(),
            "frames": self._parse_frames(),
            "z_levels": self._parse_z_levels(),
            "total_images_per_channel": frames_per_channel,
            "channels": self._parse_channels(),
            "pixel_microns": self._parse_if_not_none(self.image_calibration, self._parse_calibration),
        }

        self._set_default_if_not_empty('fields_of_view')
        self._set_default_if_not_empty('frames')
        self._metadata_parsed['num_frames'] = len(self._metadata_parsed['frames'])

        self._parse_roi_metadata()
        self._parse_experiment_metadata()

        return self._metadata_parsed

    def _set_default_if_not_empty(self, entry):
        if len(self._metadata_parsed[entry]) == 0 and self._metadata_parsed['total_images_per_channel'] > 0:
            # if the file is not empty, we always have one of this entry
            self._metadata_parsed[entry] = [0]

    @staticmethod
    def _parse_if_not_none(to_check, callback):
        if to_check is not None:
            return callback()
        return None

    def _parse_width_or_height(self, key):
        return self.image_attributes[six.b('SLxImageAttributes')][six.b(key)]

    def _parse_height(self):
        return self._parse_width_or_height('uiHeight')

    def _parse_width(self):
        return self._parse_width_or_height('uiWidth')

    def _parse_date(self):
        return parse_date(self.image_text_info[six.b('SLxImageTextInfo')])

    def _parse_calibration(self):
        return self.image_calibration.get(six.b('SLxCalibration'), {}).get(six.b('dCalibration'))

    def _parse_frames(self):
        """The number of cycles.

        Returns:
            list: list of all the frame numbers
        """
        return self._parse_dimension(r""".*?T'?\((\d+)\).*?""")

    def _parse_channels(self):
        """These are labels created by the NIS Elements user. Typically they may a short description of the filter cube
        used (e.g. 'bright field', 'GFP', etc.)

        Returns:
            list: the color channels
        """
        if self.image_metadata_sequence is None:
            return []

        metadata = self.image_metadata_sequence[six.b('SLxPictureMetadata')][six.b('sPicturePlanes')]
        channels = self._process_channels_metadata(metadata)

        return channels

    def _process_channels_metadata(self, metadata):
        try:
            validity = self.image_metadata[six.b('SLxExperiment')][six.b('ppNextLevelEx')][six.b('')][0][
                six.b('ppNextLevelEx')][six.b('')][0][six.b('pItemValid')]
        except (KeyError, TypeError):
            # If none of the channels have been deleted, there is no validity list, so we just make one
            validity = [True for _ in metadata]
        # Channel information is contained in dictionaries with the keys a0, a1...an where the number
        # indicates the order in which the channel is stored. So by sorting the dicts alphabetically
        # we get the correct order.
        channels = []
        for (label, chan), valid in zip(sorted(metadata[six.b('sPlaneNew')].items()), validity):
            if not valid:
                continue
            channels.append(chan[six.b('sDescription')].decode("utf8"))
        return channels

    def _parse_fields_of_view(self):
        """The metadata contains information about fields of view, but it contains it even if some fields
        of view were cropped. We can't find anything that states which fields of view are actually
        in the image data, so we have to calculate it. There probably is something somewhere, since
        NIS Elements can figure it out, but we haven't found it yet.

        """
        return self._parse_dimension(r""".*?XY\((\d+)\).*?""")

    def _parse_z_levels(self):
        """The different levels in the Z-plane.

        Returns:
            list: the z levels, just a sequence from 0 to n.
        """
        return self._parse_dimension(r""".*?Z\((\d+)\).*?""")

    def _parse_dimension_text(self):
        """While there are metadata values that represent a lot of what we want to capture, they seem to be unreliable.
        Sometimes certain elements don't exist, or change their data type randomly. However, the human-readable text
        is always there and in the same exact format, so we just parse that instead.

        """
        dimension_text = six.b("")
        if self.image_text_info is None:
            return dimension_text

        textinfo = self.image_text_info[six.b('SLxImageTextInfo')].values()

        for line in textinfo:
            entry = self._parse_dimension_text_line(line)
            if entry is not None:
                return entry

        return dimension_text

    @staticmethod
    def _parse_dimension_text_line(line):
        if six.b("Dimensions:") in line:
            entries = line.split(six.b("\r\n"))
            for entry in entries:
                if entry.startswith(six.b("Dimensions:")):
                    return entry
        return None

    def _parse_dimension(self, pattern):
        dimension_text = self._parse_dimension_text()
        if dimension_text is None:
            return []
        if six.PY3:
            dimension_text = dimension_text.decode("utf8")
        match = re.match(pattern, dimension_text)
        if not match:
            return []
        count = int(match.group(1))
        return list(range(count))

    def _parse_total_images_per_channel(self):
        """The total number of images per channel.

        Warning: this may be inaccurate as it includes 'gap' images.

        """
        if self.image_attributes is None:
            return 0
        return self.image_attributes[six.b('SLxImageAttributes')][six.b('uiSequenceCount')]

    def _parse_roi_metadata(self):
        """Parse the raw ROI metadata.

        """
        if self.roi_metadata is None or not six.b('RoiMetadata_v1') in self.roi_metadata:
            return

        raw_roi_data = self.roi_metadata[six.b('RoiMetadata_v1')]

        if not six.b('m_vectGlobal_Size') in raw_roi_data:
            return

        number_of_rois = raw_roi_data[six.b('m_vectGlobal_Size')]

        roi_objects = []
        for i in range(number_of_rois):
            current_roi = raw_roi_data[six.b('m_vectGlobal_%d' % i)]
            roi_objects.append(self._parse_roi(current_roi))

        self._metadata_parsed['rois'] = roi_objects

    def _parse_roi(self, raw_roi_dict):
        """Extract the vector animation parameters from the ROI.

        This includes the position and size at the given timepoints.

        Args:
            raw_roi_dict: dictionary of raw roi metadata

        Returns:
            dict: the parsed ROI metadata

        """
        number_of_timepoints = raw_roi_dict[six.b('m_vectAnimParams_Size')]

        roi_dict = {
            "timepoints": [],
            "positions": [],
            "sizes": [],
            "shape": self._parse_roi_shape(raw_roi_dict[six.b('m_sInfo')][six.b('m_uiShapeType')]),
            "type": self._parse_roi_type(raw_roi_dict[six.b('m_sInfo')][six.b('m_uiInterpType')])
        }
        for i in range(number_of_timepoints):
            roi_dict = self._parse_vect_anim(roi_dict, raw_roi_dict[six.b('m_vectAnimParams_%d' % i)])

        # convert to NumPy arrays
        roi_dict["timepoints"] = np.array(roi_dict["timepoints"], dtype=np.float)
        roi_dict["positions"] = np.array(roi_dict["positions"], dtype=np.float)
        roi_dict["sizes"] = np.array(roi_dict["sizes"], dtype=np.float)

        return roi_dict

    @staticmethod
    def _parse_roi_shape(shape):
        if shape == 3:
            return 'rectangle'
        elif shape == 9:
            return 'circle'

        return None

    @staticmethod
    def _parse_roi_type(type_no):
        if type_no == 4:
            return 'stimulation'
        elif type_no == 3:
            return 'reference'
        elif type_no == 2:
            return 'background'

        return None

    def _parse_vect_anim(self, roi_dict, animation_dict):
        """
        Parses a ROI vector animation object and adds it to the global list of timepoints and positions.

        Args:
            roi_dict: the raw roi dictionary
            animation_dict: the raw animation dictionary

        Returns:
            dict: the parsed metadata

        """
        roi_dict["timepoints"].append(animation_dict[six.b('m_dTimeMs')])

        image_width = self._metadata_parsed["width"] * self._metadata_parsed["pixel_microns"]
        image_height = self._metadata_parsed["height"] * self._metadata_parsed["pixel_microns"]

        # positions are taken from the center of the image as a fraction of the half width/height of the image
        position = np.array((0.5 * image_width * (1 + animation_dict[six.b('m_dCenterX')]),
                             0.5 * image_height * (1 + animation_dict[six.b('m_dCenterY')]),
                             animation_dict[six.b('m_dCenterZ')]))
        roi_dict["positions"].append(position)

        size_dict = animation_dict[six.b('m_sBoxShape')]

        # sizes are fractions of the half width/height of the image
        roi_dict["sizes"].append((size_dict[six.b('m_dSizeX')] * 0.25 * image_width,
                                  size_dict[six.b('m_dSizeY')] * 0.25 * image_height,
                                  size_dict[six.b('m_dSizeZ')]))
        return roi_dict

    def _parse_experiment_metadata(self):
        """Parse the metadata of the ND experiment

        """
        if self.image_metadata is None or six.b('SLxExperiment') not in self.image_metadata:
            return

        raw_data = self.image_metadata[six.b('SLxExperiment')]

        experimental_data = {
            'description': 'unknown',
            'loops': []
        }

        if six.b('wsApplicationDesc') in raw_data:
            experimental_data['description'] = raw_data[six.b('wsApplicationDesc')].decode('utf8')

        if six.b('uLoopPars') in raw_data:
            experimental_data['loops'] = self._parse_loop_data(raw_data[six.b('uLoopPars')])

        self._metadata_parsed['experiment'] = experimental_data

    @staticmethod
    def _get_loops_from_data(loop_data):
        loops = [loop_data]
        if six.b('uiPeriodCount') in loop_data and loop_data[six.b('uiPeriodCount')] > 0:
            # special ND experiment
            if six.b('pPeriod') not in loop_data:
                return []

            # take the first dictionary element, it contains all loop data
            loops = loop_data[six.b('pPeriod')][list(loop_data[six.b('pPeriod')].keys())[0]]
        return loops

    def _parse_loop_data(self, loop_data):
        """Parse the experimental loop data

        Args:
            loop_data: dictionary of experiment loops

        Returns:
            list: list of the parsed loops

        """
        loops = self._get_loops_from_data(loop_data)

        # take into account the absolute time in ms
        time_offset = 0

        parsed_loops = []

        for loop in loops:
            # duration of this loop
            duration = get_from_dict_if_exists('dDuration', loop) or 0

            # uiLoopType == 6 is a stimulation loop
            is_stimulation = get_from_dict_if_exists('uiLoopType', loop) == 6

            interval = self._determine_sampling_interval(duration, loop)

            parsed_loop = {
                'start': time_offset,
                'duration': duration,
                'stimulation': is_stimulation,
                'sampling_interval': interval
            }

            parsed_loops.append(parsed_loop)

            # increase the time offset
            time_offset += duration

        return parsed_loops

    @staticmethod
    def _determine_sampling_interval(duration, loop):
        """Determines the loop sampling interval in milliseconds

        Args:
            duration: loop duration in milliseconds
            loop: loop dictionary

        Returns:
            float: the sampling interval in milliseconds

        """
        interval = get_from_dict_if_exists('dPeriod', loop)
        if interval is None or interval <= 0:
            # Use a fallback if it is still not found
            interval = get_from_dict_if_exists('dAvgPeriodDiff', loop)
        if interval is None or interval <= 0:
            # In some cases, both keys are not saved. Then try to calculate it.
            number_of_loops = get_from_dict_if_exists('uiCount', loop)
            number_of_loops = number_of_loops if number_of_loops > 0 else 1
            interval = duration / number_of_loops
        return interval

    @property
    def image_text_info(self):
        """Textual image information

        Returns:
            dict: containing the textual image info

        """
        return read_metadata(read_chunk(self._fh, self._label_map.image_text_info), 1)

    @property
    def image_metadata_sequence(self):
        """Image metadata of the sequence

        Returns:
            dict: containing the metadata

        """
        return read_metadata(read_chunk(self._fh, self._label_map.image_metadata_sequence), 1)

    @property
    def image_calibration(self):
        """The amount of pixels per micron.

        Returns:
            dict: pixels per micron
        """
        return read_metadata(read_chunk(self._fh, self._label_map.image_calibration), 1)

    @property
    def image_attributes(self):
        """Image attributes

        Returns:
            dict: containing the image attributes
        """
        return read_metadata(read_chunk(self._fh, self._label_map.image_attributes), 1)

    @property
    def x_data(self):
        """X data

        Returns:
            dict: x_data
        """
        return read_array(self._fh, 'double', self._label_map.x_data)

    @property
    def y_data(self):
        """Y data

        Returns:
            dict: y_data
        """
        return read_array(self._fh, 'double', self._label_map.y_data)

    @property
    def z_data(self):
        """Z data

        Returns:
            dict: z_data
        """
        return read_array(self._fh, 'double', self._label_map.z_data)

    @property
    def roi_metadata(self):
        """Contains information about the defined ROIs: shape, position and type (reference/background/stimulation).

        Returns:
            dict: ROI metadata dictionary
        """
        return read_metadata(read_chunk(self._fh, self._label_map.roi_metadata), 1)

    @property
    def pfs_status(self):
        """Perfect focus system (PFS) status

        Returns:
            dict: Perfect focus system (PFS) status

        """
        return read_array(self._fh, 'int', self._label_map.pfs_status)

    @property
    def pfs_offset(self):
        """Perfect focus system (PFS) offset

        Returns:
            dict: Perfect focus system (PFS) offset

        """
        return read_array(self._fh, 'int', self._label_map.pfs_offset)

    @property
    def camera_exposure_time(self):
        """Exposure time information

        Returns:
            dict: Camera exposure time

        """
        return read_array(self._fh, 'double', self._label_map.camera_exposure_time)

    @property
    def lut_data(self):
        """LUT information

        Returns:
            dict: LUT information

        """
        return xmltodict.parse(read_chunk(self._fh, self._label_map.lut_data))

    @property
    def grabber_settings(self):
        """Grabber settings

        Returns:
            dict: Acquisition settings

        """
        return xmltodict.parse(read_chunk(self._fh, self._label_map.grabber_settings))

    @property
    def custom_data(self):
        """Custom user data

        Returns:
            dict: custom user data

        """
        return xmltodict.parse(read_chunk(self._fh, self._label_map.custom_data))

    @property
    def app_info(self):
        """NIS elements application info

        Returns:
            dict: (Version) information of the NIS Elements application

        """
        return xmltodict.parse(read_chunk(self._fh, self._label_map.app_info))

    @property
    def camera_temp(self):
        """Camera temperature

        Yields:
            float: the temperature

        """
        camera_temp = read_array(self._fh, 'double', self._label_map.camera_temp)
        if camera_temp:
            for temp in map(lambda x: round(x * 100.0, 2), camera_temp):
                yield temp

    @property
    def acquisition_times(self):
        """Acquisition times

        Yields:
            float: the acquisition time

        """
        acquisition_times = read_array(self._fh, 'double', self._label_map.acquisition_times)
        if acquisition_times:
            for acquisition_time in map(lambda x: x / 1000.0, acquisition_times):
                yield acquisition_time

    @property
    def image_metadata(self):
        """Image metadata

        Returns:
            dict: Extra image metadata

        """
        if self._label_map.image_metadata:
            return read_metadata(read_chunk(self._fh, self._label_map.image_metadata), 1)
