"""Functions to create artificial nd2 data for testing purposes
"""
import six
import numpy as np
import struct


class ArtificialND2(object):
    """Artificial ND2 class (for testing purposes)
    """

    def __init__(self, file, version=(3, 0)):
        self._fh = open(file, 'wb')
        self.write_version(version)

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

    def write_version(self, version=(3, 0)):
        """Write file header
        """
        # write 16 empty bytes
        self._fh.write(bytearray(16))

        # write version info
        version_info = six.b('ND2 FILE SIGNATURE CHUNK NAME01!Ver%s.%s' % version)
        self._fh.write(version_info)

    @staticmethod
    def create_label_map_bytes():
        """Construct a binary label map

        Returns:
            tuple: (binary data, dictionary data)

        """
        raw_text = six.b('')
        labels = {
            'image_attributes': "ImageAttributesLV!",
            'image_text_info': "ImageTextInfoLV!",
            'image_metadata': "ImageMetadataLV!",
            'image_metadata_sequence': "ImageMetadataSeqLV|0!",
            'image_calibration': "ImageCalibrationLV|0!",
            'x_data': "CustomData|X!",
            'y_data': "CustomData|Y!",
            'z_data': "CustomData|Z!",
            'roi_metadata': "CustomData|RoiMetadata_v1!",
            'pfs_status': "CustomData|PFS_STATUS!",
            'pfs_offset': "CustomData|PFS_OFFSET!",
            'guid': "CustomData|GUIDStore!",
            'description': "CustomData|CustomDescriptionV1_0!",
            'camera_exposure_time': "CustomData|Camera_ExposureTime1!",
            'camera_temp': "CustomData|CameraTemp1!",
            'acquisition_times': "CustomData|AcqTimesCache!",
            'acquisition_times_2': "CustomData|AcqTimes2Cache!",
            'acquisition_frames': "CustomData|AcqFramesCache!",
            'lut_data': "CustomDataVar|LUTDataV1_0!",
            'grabber_settings': "CustomDataVar|GrabberCameraSettingsV1_0!",
            'custom_data': "CustomDataVar|CustomDataV2_0!",
            'app_info': "CustomDataVar|AppInfo_V1_0!",
            'image_frame_0': "ImageDataSeq|0!"
        }
        data = {}

        # generate random positions and lengths
        lengths = np.random.random_integers(1, 999, len(labels))
        positions = np.subtract(np.cumsum(lengths), lengths[0])

        for length, pos, label in zip(lengths, positions, labels):
            raw_text += six.b(labels[label])
            raw_text += struct.pack('QQ', pos, length)
            data[label] = (pos, length)

        return raw_text, data
