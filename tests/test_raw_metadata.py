import unittest
from nd2reader.raw_metadata import RawMetadata


class TestRawMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = RawMetadata(None, None)

    def test_parse_roi_shape(self):
        self.assertEqual(self.metadata._parse_roi_shape(3), 'rectangle')
        self.assertEqual(self.metadata._parse_roi_shape(9), 'circle')
        self.assertIsNone(self.metadata._parse_roi_shape(-1))

    def test_parse_roi_type(self):
        self.assertEqual(self.metadata._parse_roi_type(3), 'reference')
        self.assertEqual(self.metadata._parse_roi_type(2), 'background')
        self.assertEqual(self.metadata._parse_roi_type(4), 'stimulation')
        self.assertIsNone(self.metadata._parse_roi_type(-1))
