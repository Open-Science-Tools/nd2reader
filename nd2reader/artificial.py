"""Functions to create artificial nd2 data for testing purposes
"""
import six
import numpy as np
import struct
from nd2reader.common import check_or_make_dir
from os import path

global_labels = ['image_attributes', 'image_text_info', 'image_metadata',
                 'image_metadata_sequence', 'image_calibration', 'x_data',
                 'y_data', 'z_data', 'roi_metadata', 'pfs_status', 'pfs_offset',
                 'guid', 'description', 'camera_exposure_time', 'camera_temp',
                 'acquisition_times', 'acquisition_times_2',
                 'acquisition_frames', 'lut_data', 'grabber_settings',
                 'custom_data', 'app_info', 'image_frame_0']

global_file_labels = ["ImageAttributesLV!", "ImageTextInfoLV!",
                      "ImageMetadataLV!", "ImageMetadataSeqLV|0!",
                      "ImageCalibrationLV|0!", "CustomData|X!", "CustomData|Y!",
                      "CustomData|Z!", "CustomData|RoiMetadata_v1!",
                      "CustomData|PFS_STATUS!", "CustomData|PFS_OFFSET!",
                      "CustomData|GUIDStore!", "CustomData|CustomDescriptionV1_0!",
                      "CustomData|Camera_ExposureTime1!", "CustomData|CameraTemp1!",
                      "CustomData|AcqTimesCache!", "CustomData|AcqTimes2Cache!",
                      "CustomData|AcqFramesCache!", "CustomDataVar|LUTDataV1_0!",
                      "CustomDataVar|GrabberCameraSettingsV1_0!",
                      "CustomDataVar|CustomDataV2_0!", "CustomDataVar|AppInfo_V1_0!",
                      "ImageDataSeq|0!"]


class ArtificialND2(object):
    """Artificial ND2 class (for testing purposes)
    """
    header = 0xabeceda
    relative_offset = 0
    data_types = {'unsigned_char': 1,
                  'unsigned_int': 2,
                  'unsigned_int_2': 3,
                  'unsigned_long': 5,
                  'double': 6,
                  'string': 8,
                  'char_array': 9,
                  'metadata_item': 11,
                  }

    def __init__(self, file, version=(3, 0), skip_blocks=None):
        self.version = version
        self.raw_text, self.locations, self.data = b'', None, None
        check_or_make_dir(path.dirname(file))
        self._fh = open(file, 'w+b', 0)
        self.write_file(skip_blocks)

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

    def write_file(self, skip_blocks=None):
        if skip_blocks is None:
            skip_blocks = []

        if 'version' not in skip_blocks:
            # write version header at start of the file
            self.write_version()

        if 'label_map' not in skip_blocks:
            # write label map + data in the center
            self.locations, self.data = self.write_label_map()

        if 'label_map_marker' not in skip_blocks:
            # write start position of label map at the end of the file
            self.write_label_map_info()

        # write all to file
        self._fh.write(self.raw_text)

    def write_version(self):
        """Write file header
        """
        # write 16 empty bytes
        self.raw_text += bytearray(16)

        # write version info
        self.raw_text += self._get_version_string()

    def write_label_map_info(self):
        """Write the location of the start of the label map at the end of the file
        """
        location = self._get_version_byte_length()
        self.raw_text += struct.pack("Q", location)

    def _get_version_string(self):
        return six.b('ND2 FILE SIGNATURE CHUNK NAME01!Ver%s.%s' % self.version)

    def _get_version_byte_length(self):
        return 16 + len(self._get_version_string())

    def write_label_map(self):
        raw_text, locations, data = self.create_label_map_bytes()
        self.raw_text += raw_text

        return locations, data

    def create_label_map_bytes(self):
        """Construct a binary label map

        Returns:
            tuple: (binary data, dictionary data)

        """
        raw_text = six.b('')
        labels = global_labels
        file_labels = global_file_labels

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
        packed_data = self._pack_raw_data_with_metadata(data)

        raw_data = struct.pack("IIQ", self.header, self.relative_offset, len(packed_data))
        raw_data += packed_data

        return raw_data

    def _pack_raw_data_with_metadata(self, data):
        raw_data = b''

        if isinstance(data, dict):
            raw_data = self._pack_dict_with_metadata(data)
        elif isinstance(data, int):
            raw_data = struct.pack('I', data)
        elif isinstance(data, float):
            raw_data = struct.pack('d', data)
        elif isinstance(data, str):
            raw_data = self._str_to_padded_bytes(data)

        return raw_data

    def _get_data_type(self, data):
        if isinstance(data, dict):
            return self.data_types['metadata_item']
        elif isinstance(data, int):
            return self.data_types['unsigned_int']
        elif isinstance(data, str):
            return self.data_types['string']
        else:
            return self.data_types['double']

    @staticmethod
    def _str_to_padded_bytes(data):
        return six.b('').join([struct.pack('cx', six.b(s)) for s in data]) + struct.pack('xx')

    def _pack_dict_with_metadata(self, data):
        raw_data = b''

        for data_key in data.keys():
            # names have always one character extra and are padded in zero bytes???
            b_data_key = self._str_to_padded_bytes(data_key)

            # header consists of data type and length of key name, it is represented by 2 unsigned chars
            raw_data += struct.pack('BB', self._get_data_type(data[data_key]), len(data_key) + 1)
            raw_data += b_data_key

            sub_data = self._pack_raw_data_with_metadata(data[data_key])

            if isinstance(data[data_key], dict):
                # Pack: the number of keys and the length of raw data until now, sub data
                # and the 12 bytes that we add now
                raw_data += struct.pack("<IQ", len(data[data_key].keys()), len(sub_data) + len(raw_data) + 12)

            raw_data += sub_data

            if isinstance(data[data_key], dict):
                # apparently there is also a huge empty space
                raw_data += b''.join([struct.pack('x')] * len(data[data_key].keys()) * 8)

        return raw_data

    @staticmethod
    def _get_slx_img_attrib():
        return {'uiWidth': 128,
                'uiWidthBytes': 256,
                'uiHeight': 128,
                'uiComp': 1,
                'uiBpcInMemory': 16,
                'uiBpcSignificant': 12,
                'uiSequenceCount': 70,
                'uiTileWidth': 128,
                'uiTileHeight': 128,
                'eCompression': 2,
                'dCompressionParam': -1.0,
                'ePixelType': 1,
                'uiVirtualComponents': 1
                }

    @staticmethod
    def _get_slx_picture_metadata():
        return {'sPicturePlanes':
                {
                    'sPlaneNew': {
                        # channels are numbered a0, a1, ..., aN
                        'a0': {
                            'sDescription': 'TRITC'
                            }
                        }
                    }
                }

    def _get_file_data(self, labels):
        file_data = [
            {'SLxImageAttributes': self._get_slx_img_attrib()},  # ImageAttributesLV!",
            7,  # ImageTextInfoLV!",
            7,  # ImageMetadataLV!",
            {'SLxPictureMetadata': self._get_slx_picture_metadata()},  # ImageMetadataSeqLV|0!",
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
            [0],  # CustomData|AcqTimesCache!",
            [0],  # CustomData|AcqTimes2Cache!",
            [0],  # CustomData|AcqFramesCache!",
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
