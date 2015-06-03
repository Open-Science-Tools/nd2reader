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

    def test_calculate_field_of_view_two_channels(self):
        nd2 = MockNd2Parser(['', 'GFP'], [0], [0])
        for frame_number in range(1000):
            result = Nd2Parser._calculate_field_of_view(nd2, frame_number)
            self.assertEqual(result, 0)

    def test_calculate_field_of_view_three_channels(self):
        nd2 = MockNd2Parser(['', 'GFP', 'dsRed'], [0], [0])
        for frame_number in range(1000):
            result = Nd2Parser._calculate_field_of_view(nd2, frame_number)
            self.assertEqual(result, 0)

    def test_calculate_field_of_view_two_fovs(self):
        nd2 = MockNd2Parser([''], [0, 1], [0])
        for frame_number in range(1000):
            result = Nd2Parser._calculate_field_of_view(nd2, frame_number)
            self.assertEqual(result, frame_number % 2)

    def test_calculate_field_of_view_two_fovs_two_zlevels(self):
        nd2 = MockNd2Parser([''], [0, 1], [0, 1])
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 0), 0)
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 1), 0)
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 2), 1)
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 3), 1)
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 4), 0)
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 5), 0)
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 6), 1)
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 7), 1)

    def test_calculate_field_of_view_two_everything(self):
        nd2 = MockNd2Parser(['', 'GFP'], [0, 1], [0, 1])
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 0), 0)
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 1), 0)
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 2), 0)
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 3), 0)
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 4), 1)
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 5), 1)
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 6), 1)
        self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 7), 1)

    def test_calculate_field_of_view_7c2f2z(self):
        nd2 = MockNd2Parser(['', 'GFP', 'dsRed', 'dTomato', 'lulzBlue', 'jimbotronPurple', 'orange'], [0, 1], [0, 1])
        for i in range(14):
            self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 0)
        for i in range(14, 28):
            self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 1)
        for i in range(28, 42):
            self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 0)
        for i in range(42, 56):
            self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 1)
        for i in range(56, 70):
            self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 0)
        for i in range(70, 84):
            self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 1)

    def test_calculate_channel_simple(self):








