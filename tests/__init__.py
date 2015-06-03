from nd2reader.parser import Nd2Parser
import unittest


class MockNd2Parser(object):
    def __init__(self, channels, fields_of_view, z_levels):
        self.channels = channels
        self.fields_of_view = fields_of_view
        self.z_levels = z_levels


class TestNd2Parser(unittest.TestCase):
    def test_calculate_field_of_view_simple(self):
        """ With a single field of view, the field of view should always be the same number (0). """
        nd2 = MockNd2Parser([''], [0], [0])
        for frame_number in range(1000):
            result = Nd2Parser._calculate_field_of_view(nd2, frame_number)
            self.assertEqual(result, 0)

