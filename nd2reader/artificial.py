"""Functions to create artificial nd2 data for testing purposes
"""
import six
import numpy as np
import struct
from nd2reader.common import check_or_make_dir
from os import path


class ArtificialND2(object):
    """Artificial ND2 class (for testing purposes)
    """
    header = 0xabeceda
    relative_offset = 0

    def __init__(self, file, version=(3, 0)):
        self.version = version
        self.raw_text, self.locations, self.data = None, None, None
        check_or_make_dir(path.dirname(file))
        self._fh = open(file, 'w+b', 0)
        self.write_file()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @property
    def file_handle(self):
        """The file handle to the binary file

        Returns:
            file: the file handle

        """
        return self._fh

    def close(self):
        """Correctly close the file handle
        """
        if self._fh is not None:
            self._fh.close()

    def write_file(self):
        self.write_version()
        self.raw_text, self.locations, self.data = self.write_label_map()

    def write_version(self):
        """Write file header
        """
        # write 16 empty bytes
        self._fh.write(bytearray(16))

        # write version info
        self._fh.write(self._get_version_string())

    def _get_version_string(self):
        return six.b('ND2 FILE SIGNATURE CHUNK NAME01!Ver%s.%s' % self.version)

    def _get_version_byte_length(self):
        return 16 + len(self._get_version_string())

    def write_label_map(self):
        raw_text, locations, data = self.create_label_map_bytes()
        self._fh.write(raw_text)

        return raw_text, locations, data

    def create_label_map_bytes(self):
        """Construct a binary label map

        Returns:
            tuple: (binary data, dictionary data)

        """
        raw_text = six.b('')
        labels = [
            'image_attributes',
            'image_text_info',
            'image_metadata',
            'image_metadata_sequence',
            'image_calibration',
            'x_data',
            'y_data',
            'z_data',
            'roi_metadata',
            'pfs_status',
            'pfs_offset',
            'guid',
            'description',
            'camera_exposure_time',
            'camera_temp',
            'acquisition_times',
            'acquisition_times_2',
            'acquisition_frames',
            'lut_data',
            'grabber_settings',
            'custom_data',
            'app_info',
            'image_frame_0'
        ]
        file_labels = [
            "ImageAttributesLV!",
            "ImageTextInfoLV!",
            "ImageMetadataLV!",
            "ImageMetadataSeqLV|0!",
            "ImageCalibrationLV|0!",
            "CustomData|X!",
            "CustomData|Y!",
            "CustomData|Z!",
            "CustomData|RoiMetadata_v1!",
            "CustomData|PFS_STATUS!",
            "CustomData|PFS_OFFSET!",
            "CustomData|GUIDStore!",
            "CustomData|CustomDescriptionV1_0!",
            "CustomData|Camera_ExposureTime1!",
            "CustomData|CameraTemp1!",
            "CustomData|AcqTimesCache!",
            "CustomData|AcqTimes2Cache!",
            "CustomData|AcqFramesCache!",
            "CustomDataVar|LUTDataV1_0!",
            "CustomDataVar|GrabberCameraSettingsV1_0!",
            "CustomDataVar|CustomDataV2_0!",
            "CustomDataVar|AppInfo_V1_0!",
            "ImageDataSeq|0!"
        ]

        file_data, file_data_dict = self._get_file_data(labels)

        locations = {}

        # generate random positions and lengths
        version_length = self._get_version_byte_length()

        # calculate data length
        label_length = np.sum([len(six.b(l)) + 16 for l in file_labels])

        # write label map
        cur_pos = version_length + label_length
        for label, file_label, data in zip(labels, file_labels, file_data):
            raw_text += six.b(file_label)
            data_length = len(data)
            raw_text += struct.pack('QQ', cur_pos, data_length)
            locations[label] = (cur_pos, data_length)
            cur_pos += data_length

        # write data
        raw_text += six.b('').join(file_data)

        return raw_text, locations, file_data_dict

    def _pack_data_with_metadata(self, data):
        data = struct.pack('I', data)
        raw_data = struct.pack("IIQ", self.header, self.relative_offset, len(data))
        raw_data += data
        return raw_data

    def _get_file_data(self, labels):
        file_data = [
            7,  # ImageAttributesLV!",
            7,  # ImageTextInfoLV!",
            7,  # ImageMetadataLV!",
            7,  # ImageMetadataSeqLV|0!",
            7,  # ImageCalibrationLV|0!",
            7,  # CustomData|X!",
            7,  # CustomData|Y!",
            7,  # CustomData|Z!",
            7,  # CustomData|RoiMetadata_v1!",
            7,  # CustomData|PFS_STATUS!",
            7,  # CustomData|PFS_OFFSET!",
            7,  # CustomData|GUIDStore!",
            7,  # CustomData|CustomDescriptionV1_0!",
            7,  # CustomData|Camera_ExposureTime1!",
            7,  # CustomData|CameraTemp1!",
            7,  # CustomData|AcqTimesCache!",
            7,  # CustomData|AcqTimes2Cache!",
            7,  # CustomData|AcqFramesCache!",
            7,  # CustomDataVar|LUTDataV1_0!",
            7,  # CustomDataVar|GrabberCameraSettingsV1_0!",
            7,  # CustomDataVar|CustomDataV2_0!",
            7,  # CustomDataVar|AppInfo_V1_0!",
            7,  # ImageDataSeq|0!"
        ]

        file_data_dict = {l: d for l, d in zip(labels, file_data)}

        # convert to bytes
        file_data = [self._pack_data_with_metadata(d) for d in file_data]

        return file_data, file_data_dict
