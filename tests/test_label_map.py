import unittest
from nd2reader.label_map import LabelMap
from nd2reader.artificial import ArtificialND2


class TestLabelMap(unittest.TestCase):
    def setUp(self):
        self.raw_text, self.locations = ArtificialND2.create_label_map_bytes()
        self.label_map = LabelMap(self.raw_text)

    def test_image_text_info(self):
        self.assertEqual(self.locations['image_text_info'][0], self.label_map.image_text_info)

    def test_image_metadata(self):
        self.assertEqual(self.locations['image_metadata'][0], self.label_map.image_metadata)

    def test_image_attributes(self):
        self.assertEqual(self.locations['image_attributes'][0], self.label_map.image_attributes)

    def test_image_metadata_sequence(self):
        self.assertEqual(self.locations['image_metadata_sequence'][0], self.label_map.image_metadata_sequence)

    def test_image_calibration(self):
        self.assertEqual(self.locations['image_calibration'][0], self.label_map.image_calibration)

    def test_x_data(self):
        self.assertEqual(self.locations['x_data'][0], self.label_map.x_data)

    def test_y_data(self):
        self.assertEqual(self.locations['y_data'][0], self.label_map.y_data)

    def test_z_data(self):
        self.assertEqual(self.locations['z_data'][0], self.label_map.z_data)

    def test_roi_metadata(self):
        self.assertEqual(self.locations['roi_metadata'][0], self.label_map.roi_metadata)

    def test_pfs_status(self):
        self.assertEqual(self.locations['pfs_status'][0], self.label_map.pfs_status)

    def test_pfs_offset(self):
        self.assertEqual(self.locations['pfs_offset'][0], self.label_map.pfs_offset)

    def test_guid(self):
        self.assertEqual(self.locations['guid'][0], self.label_map.guid)

    def test_description(self):
        self.assertEqual(self.locations['description'][0], self.label_map.description)

    def test_camera_exposure_time(self):
        self.assertEqual(self.locations['camera_exposure_time'][0], self.label_map.camera_exposure_time)

    def test_camera_temp(self):
        self.assertEqual(self.locations['camera_temp'][0], self.label_map.camera_temp)

    def test_acquisition_times(self):
        self.assertEqual(self.locations['acquisition_times'][0], self.label_map.acquisition_times)

    def test_acquisition_times_2(self):
        self.assertEqual(self.locations['acquisition_times_2'][0], self.label_map.acquisition_times_2)

    def test_acquisition_frames(self):
        self.assertEqual(self.locations['acquisition_frames'][0], self.label_map.acquisition_frames)

    def test_lut_data(self):
        self.assertEqual(self.locations['lut_data'][0], self.label_map.lut_data)

    def test_grabber_settings(self):
        self.assertEqual(self.locations['grabber_settings'][0], self.label_map.grabber_settings)

    def test_custom_data(self):
        self.assertEqual(self.locations['custom_data'][0], self.label_map.custom_data)

    def test_app_info(self):
        self.assertEqual(self.locations['app_info'][0], self.label_map.app_info)
