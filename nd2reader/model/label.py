import six
import struct
from collections import namedtuple
import re


data_location = namedtuple("DataLocation", ["location", "length"])


class LabelMap(object):
    """
    """
    def __init__(self, raw_binary_data):
        self._data = raw_binary_data

    def _get_location(self, label):
        try:
            label_location = self._data.index(label) + len(label)
            return self._parse_data_location(label_location)
        except ValueError:
            return None

    def _parse_data_location(self, label_location):
        location, length = struct.unpack("QQ", self._data[label_location: label_location + 16])
        return data_location(location=location, length=length)

    @property
    def image_text_info(self):
        return self._get_location(six.b("ImageTextInfoLV!"))

    @property
    def image_metadata_sequence(self):
        # there is always only one of these, even though it has a pipe followed by a zero, which is how they do indexes
        return self._get_location(six.b("ImageMetadataSeqLV|0!"))

    @property
    def image_data(self):
        image_data = {}
        regex = re.compile(six.b("""ImageDataSeq\|(\d+)!"""))
        for match in regex.finditer(self._data):
            if match:
                print(match.start(), match.end())
                location = self._parse_data_location(match.end())
                image_data[int(match.group(1))] = location
        return image_data

    @property
    def image_calibration(self):
        return self._get_location(six.b("ImageCalibrationLV|0!"))

    @property
    def image_attributes(self):
        return self._get_location(six.b("ImageAttributesLV!"))

    @property
    def x_data(self):
        return self._get_location(six.b("CustomData|X!"))

    @property
    def y_data(self):
        return self._get_location(six.b("CustomData|Y!"))

    @property
    def z_data(self):
        return self._get_location(six.b("CustomData|Z!"))

    @property
    def roi_metadata(self):
        return self._get_location(six.b("CustomData|RoiMetadata_v1!"))

    @property
    def pfs_status(self):
        return self._get_location(six.b("CustomData|PFS_STATUS!"))

    @property
    def pfs_offset(self):
        return self._get_location(six.b("CustomData|PFS_OFFSET!"))

    @property
    def guid(self):
        return self._get_location(six.b("CustomData|GUIDStore!"))

    @property
    def description(self):
        return self._get_location(six.b("CustomData|CustomDescriptionV1_0!"))

    @property
    def camera_exposure_time(self):
        return self._get_location(six.b("CustomData|Camera_ExposureTime1!"))

    @property
    def camera_temp(self):
        return self._get_location(six.b("CustomData|CameraTemp1!"))

    @property
    def acquisition_times(self):
        return self._get_location(six.b("CustomData|AcqTimesCache!"))

    @property
    def acquisition_times_2(self):
        return self._get_location(six.b("CustomData|AcqTimes2Cache!"))

    @property
    def acquisition_frames(self):
        return self._get_location(six.b("CustomData|AcqFramesCache!"))

    @property
    def lut_data(self):
        return self._get_location(six.b("CustomDataVar|LUTDataV1_0!"))

    @property
    def grabber_settings(self):
        return self._get_location(six.b("CustomDataVar|GrabberCameraSettingsV1_0!"))

    @property
    def custom_data(self):
        return self._get_location(six.b("CustomDataVar|CustomDataV2_0!"))

    @property
    def app_info(self):
        return self._get_location(six.b("CustomDataVar|AppInfo_V1_0!"))
