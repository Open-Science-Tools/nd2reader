# from nd2reader.parser import Nd2Parser
# import unittest
#
#
# class MockNd2Parser(object):
#     def __init__(self, channels, fields_of_view, z_levels):
#         self.channels = channels
#         self.fields_of_view = fields_of_view
#         self.z_levels = z_levels
#
#
# class TestNd2Parser(unittest.TestCase):
#     def test_calculate_field_of_view_simple(self):
#         """ With a single field of view, the field of view should always be the same number (0). """
#         nd2 = MockNd2Parser([''], [0], [0])
#         for frame_number in range(1000):
#             result = Nd2Parser._calculate_field_of_view(nd2, frame_number)
#             self.assertEqual(result, 0)
#
#     def test_calculate_field_of_view_two_channels(self):
#         nd2 = MockNd2Parser(['', 'GFP'], [0], [0])
#         for frame_number in range(1000):
#             result = Nd2Parser._calculate_field_of_view(nd2, frame_number)
#             self.assertEqual(result, 0)
#
#     def test_calculate_field_of_view_three_channels(self):
#         nd2 = MockNd2Parser(['', 'GFP', 'dsRed'], [0], [0])
#         for frame_number in range(1000):
#             result = Nd2Parser._calculate_field_of_view(nd2, frame_number)
#             self.assertEqual(result, 0)
#
#     def test_calculate_field_of_view_two_fovs(self):
#         nd2 = MockNd2Parser([''], [0, 1], [0])
#         for frame_number in range(1000):
#             result = Nd2Parser._calculate_field_of_view(nd2, frame_number)
#             self.assertEqual(result, frame_number % 2)
#
#     def test_calculate_field_of_view_two_fovs_two_zlevels(self):
#         nd2 = MockNd2Parser([''], [0, 1], [0, 1])
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 0), 0)
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 1), 0)
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 2), 1)
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 3), 1)
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 4), 0)
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 5), 0)
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 6), 1)
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 7), 1)
#
#     def test_calculate_field_of_view_two_everything(self):
#         nd2 = MockNd2Parser(['', 'GFP'], [0, 1], [0, 1])
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 0), 0)
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 1), 0)
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 2), 0)
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 3), 0)
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 4), 1)
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 5), 1)
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 6), 1)
#         self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, 7), 1)
#
#     def test_calculate_field_of_view_7c2f2z(self):
#         nd2 = MockNd2Parser(['', 'GFP', 'dsRed', 'dTomato', 'lulzBlue', 'jimbotronPurple', 'orange'], [0, 1], [0, 1])
#         for i in range(14):
#             self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 0)
#         for i in range(14, 28):
#             self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 1)
#         for i in range(28, 42):
#             self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 0)
#         for i in range(42, 56):
#             self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 1)
#         for i in range(56, 70):
#             self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 0)
#         for i in range(70, 84):
#             self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 1)
#
#     def test_calculate_field_of_view_2c3f5z(self):
#         """ All prime numbers to elucidate any errors that won't show up when numbers are multiples of each other """
#         nd2 = MockNd2Parser(['', 'GFP'], [0, 1, 2], [0, 1, 2, 3, 4])
#         for i in range(10):
#             self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 0)
#         for i in range(10, 20):
#             self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 1)
#         for i in range(20, 30):
#             self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 2)
#         for i in range(30, 40):
#             self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 0)
#         for i in range(40, 50):
#             self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 1)
#         for i in range(50, 60):
#             self.assertEqual(Nd2Parser._calculate_field_of_view(nd2, i), 2)
#
#     def test_calculate_channel_simple(self):
#         nd2 = MockNd2Parser(['GFP'], [0], [0])
#         for i in range(1000):
#             self.assertEqual(Nd2Parser._calculate_channel(nd2, i), 'GFP')
#
#     def test_calculate_channel(self):
#         nd2 = MockNd2Parser(['', 'GFP', 'dsRed', 'dTomato', 'lulzBlue', 'jimbotronPurple', 'orange'], [0], [0])
#         for i in range(1000):
#             for n, channel in enumerate(['', 'GFP', 'dsRed', 'dTomato', 'lulzBlue', 'jimbotronPurple', 'orange'], start=i*7):
#                 self.assertEqual(Nd2Parser._calculate_channel(nd2, n), channel)
#
#     def test_calculate_channel_7c2fov1z(self):
#         nd2 = MockNd2Parser(['', 'GFP', 'dsRed', 'dTomato', 'lulzBlue', 'jimbotronPurple', 'orange'], [0, 1], [0])
#         for i in range(1000):
#             for n, channel in enumerate(['', 'GFP', 'dsRed', 'dTomato', 'lulzBlue', 'jimbotronPurple', 'orange'], start=i*7):
#                 self.assertEqual(Nd2Parser._calculate_channel(nd2, n), channel)
#
#     def test_calculate_channel_ludicrous_values(self):
#         nd2 = MockNd2Parser(['', 'GFP', 'dsRed', 'dTomato', 'lulzBlue', 'jimbotronPurple', 'orange'], list(range(31)), list(range(17)))
#         for i in range(10000):
#             for n, channel in enumerate(['', 'GFP', 'dsRed', 'dTomato', 'lulzBlue', 'jimbotronPurple', 'orange'], start=i*7):
#                 self.assertEqual(Nd2Parser._calculate_channel(nd2, n), channel)
#
#     def test_calculate_z_level(self):
#         nd2 = MockNd2Parser([''], [0], [0])
#         for frame_number in range(1000):
#             result = Nd2Parser._calculate_z_level(nd2, frame_number)
#             self.assertEqual(result, 0)
#
#     def test_calculate_z_level_1c1f2z(self):
#         nd2 = MockNd2Parser([''], [0], [0, 1])
#         for frame_number in range(1000):
#             result = Nd2Parser._calculate_z_level(nd2, frame_number)
#             self.assertEqual(result, frame_number % 2)
#
#     def test_calculate_z_level_31c17f1z(self):
#         nd2 = MockNd2Parser(list(range(31)), list(range(17)), [0])
#         for frame_number in range(1000):
#             result = Nd2Parser._calculate_z_level(nd2, frame_number)
#             self.assertEqual(result, 0)
#
#     def test_calculate_z_level_2c1f2z(self):
#         nd2 = MockNd2Parser(['', 'GFP'], [0], [0, 1])
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 0), 0)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 1), 0)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 2), 1)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 3), 1)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 4), 0)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 5), 0)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 6), 1)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 7), 1)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 8), 0)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 9), 0)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 10), 1)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 11), 1)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 12), 0)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 13), 0)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 14), 1)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 15), 1)
#
#     def test_calculate_z_level_2c3f5z(self):
#         nd2 = MockNd2Parser(['', 'GFP'], [0, 1, 2], [0, 1, 2, 3, 4])
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 0), 0)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 1), 0)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 2), 1)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 3), 1)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 4), 2)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 5), 2)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 6), 3)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 7), 3)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 8), 4)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 9), 4)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 10), 0)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 11), 0)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 12), 1)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 13), 1)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 14), 2)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 15), 2)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 16), 3)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 17), 3)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 18), 4)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 19), 4)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 20), 0)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 21), 0)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 22), 1)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 23), 1)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 24), 2)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 25), 2)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 26), 3)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 27), 3)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 28), 4)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 29), 4)
#         self.assertEqual(Nd2Parser._calculate_z_level(nd2, 30), 0)