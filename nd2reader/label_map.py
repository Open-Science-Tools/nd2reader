import six
import struct
import re


class LabelMap(object):
    """Contains pointers to metadata. This might only be valid for V3 files.

    """

    def __init__(self, raw_binary_data):
        self._data = raw_binary_data
        self._image_data = {}

    def _get_location(self, label):
        try:
            label_location = self._data.index(label) + len(label)
            return self._parse_data_location(label_location)
        except ValueError:
            return None

    def _parse_data_location(self, label_location):
        location, length = struct.unpack("QQ", self._data[label_location: label_location + 16])
        return location

    @property
    def image_text_info(self):
        """Get the location of the textual image information

        Returns:
            int: The location of the textual image information

        """
        return self._get_location(six.b("ImageTextInfoLV!"))

    @property
    def image_metadata(self):
        """Get the location of the image metadata

        Returns:
            int: The location of the image metadata

        """
        return self._get_location(six.b("ImageMetadataLV!"))

    @property
    def image_metadata_sequence(self):
        """Get the location of the image metadata sequence. There is always only one of these, even though it has a pipe
         followed by a zero, which is how they do indexes.

        Returns:
            int: The location of the image metadata sequence

        """
        return self._get_location(six.b("ImageMetadataSeqLV|0!"))

    def get_image_data_location(self, index):
        """Get the location of the image data

        Returns:
            int: The location of the image data

        """
        if not self._image_data:
            regex = re.compile(six.b("""ImageDataSeq\|(\d+)!"""))
            for match in regex.finditer(self._data):
                if match:
                    location = self._parse_data_location(match.end())
                    self._image_data[int(match.group(1))] = location
        return self._image_data[index]

    @property
    def image_calibration(self):
        """Get the location of the image calibration

        Returns:
            int: The location of the image calibration

        """
        return self._get_location(six.b("ImageCalibrationLV|0!"))

    @property
    def image_attributes(self):
        """Get the location of the image attributes

        Returns:
            int: The location of the image attributes

        """
        return self._get_location(six.b("ImageAttributesLV!"))

    @property
    def x_data(self):
        """Get the location of the custom x data

        Returns:
            int: The location of the custom x data

        """
        return self._get_location(six.b("CustomData|X!"))

    @property
    def y_data(self):
        """Get the location of the custom y data

        Returns:
            int: The location of the custom y data

        """
        return self._get_location(six.b("CustomData|Y!"))

    @property
    def z_data(self):
        """Get the location of the custom z data

        Returns:
            int: The location of the custom z data

        """
        return self._get_location(six.b("CustomData|Z!"))

    @property
    def roi_metadata(self):
        """Information about any regions of interest (ROIs) defined in the nd2 file

        Returns:
            int: The location of the regions of interest (ROIs)

        """
        return self._get_location(six.b("CustomData|RoiMetadata_v1!"))

    @property
    def pfs_status(self):
        """Get the location of the perfect focus system (PFS) status

        Returns:
            int: The location of the perfect focus system (PFS) status

        """
        return self._get_location(six.b("CustomData|PFS_STATUS!"))

    @property
    def pfs_offset(self):
        """Get the location of the perfect focus system (PFS) offset

        Returns:
            int: The location of the perfect focus system (PFS) offset

        """
        return self._get_location(six.b("CustomData|PFS_OFFSET!"))

    @property
    def guid(self):
        """Get the location of the image guid

        Returns:
            int: The location of the image guid

        """
        return self._get_location(six.b("CustomData|GUIDStore!"))

    @property
    def description(self):
        """Get the location of the image description

        Returns:
            int: The location of the image description

        """
        return self._get_location(six.b("CustomData|CustomDescriptionV1_0!"))

    @property
    def camera_exposure_time(self):
        """Get the location of the camera exposure time

        Returns:
            int: The location of the camera exposure time

        """
        return self._get_location(six.b("CustomData|Camera_ExposureTime1!"))

    @property
    def camera_temp(self):
        """Get the location of the camera temperature

        Returns:
            int: The location of the camera temperature

        """
        return self._get_location(six.b("CustomData|CameraTemp1!"))

    @property
    def acquisition_times(self):
        """Get the location of the acquisition times, block 1

        Returns:
            int: The location of the acquisition times, block 1

        """
        return self._get_location(six.b("CustomData|AcqTimesCache!"))

    @property
    def acquisition_times_2(self):
        """Get the location of the acquisition times, block 2

        Returns:
            int: The location of the acquisition times, block 2

        """
        return self._get_location(six.b("CustomData|AcqTimes2Cache!"))

    @property
    def acquisition_frames(self):
        """Get the location of the acquisition frames

        Returns:
            int: The location of the acquisition frames

        """
        return self._get_location(six.b("CustomData|AcqFramesCache!"))

    @property
    def lut_data(self):
        """Get the location of the LUT data

        Returns:
            int: The location of the LUT data

        """
        return self._get_location(six.b("CustomDataVar|LUTDataV1_0!"))

    @property
    def grabber_settings(self):
        """Get the location of the grabber settings

        Returns:
            int: The location of the grabber settings

        """
        return self._get_location(six.b("CustomDataVar|GrabberCameraSettingsV1_0!"))

    @property
    def custom_data(self):
        """Get the location of the custom user data

        Returns:
            int: The location of the custom user data

        """
        return self._get_location(six.b("CustomDataVar|CustomDataV2_0!"))

    @property
    def app_info(self):
        """Get the location of the application info metadata

        Returns:
            int: The location of the application info metadata

        """
        return self._get_location(six.b("CustomDataVar|AppInfo_V1_0!"))
