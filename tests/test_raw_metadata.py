import unittest

from nd2reader.artificial import ArtificialND2
from nd2reader.label_map import LabelMap
from nd2reader.raw_metadata import RawMetadata


class TestRawMetadata(unittest.TestCase):

    def setUp(self):
        self.raw_text, self.locations = ArtificialND2.create_label_map_bytes()
        self.label_map = LabelMap(self.raw_text)
        self.metadata = RawMetadata(None, self.label_map)

    def test_parse_roi_shape(self):
        self.assertEqual(self.metadata._parse_roi_shape(3), 'rectangle')
        self.assertEqual(self.metadata._parse_roi_shape(9), 'circle')
        self.assertIsNone(self.metadata._parse_roi_shape(-1))

    def test_parse_roi_type(self):
        self.assertEqual(self.metadata._parse_roi_type(3), 'reference')
        self.assertEqual(self.metadata._parse_roi_type(2), 'background')
        self.assertEqual(self.metadata._parse_roi_type(4), 'stimulation')
        self.assertIsNone(self.metadata._parse_roi_type(-1))

    def test_dict(self):
        self.assertTrue(type(self.metadata.__dict__) is dict)

    def test_parsed_metadata(self):
        metadata = self.metadata.get_parsed_metadata()
        self.assertTrue(type(metadata) is dict)
        required_keys = ["height", "width", "date", "fields_of_view", "frames", "z_levels", "total_images_per_channel",
                         "channels", "pixel_microns"]
        for required in required_keys:
            self.assertTrue(required in metadata)

        # it should now be stored, see if that dict is returned
        metadata['height'] = 1
        self.metadata._metadata_parsed['height'] = 1
        second_metadata = self.metadata.get_parsed_metadata()
        self.assertDictEqual(metadata, second_metadata)
