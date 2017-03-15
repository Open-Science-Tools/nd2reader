"""
Unit test for backwards compatibility.
"""
import unittest
from os import path

from nd2reader.legacy import Nd2


class TestReader(unittest.TestCase):
    def setUp(self):
        dir_path = path.dirname(path.realpath(__file__))
        self.files = [
            path.join(dir_path, 'test_data/data001.nd2'),
            path.join(dir_path, 'test_data/data002.nd2')
        ]

    def test_sizes_data_001(self):
        with Nd2(self.files[0]) as reader:
            self.assertEqual(reader.width, 128)
            self.assertEqual(reader.height, 128)
            self.assertEqual(len(reader.frames), 982)
            self.assertEqual(len(reader.channels), 1)
            self.assertEqual(len(reader.z_levels), 1)

    def test_frame_size_data_001(self):
        with Nd2(self.files[0]) as reader:
            frame = reader[13]
            self.assertEqual(frame.shape[0], 128)
            self.assertEqual(frame.shape[1], 128)

    def test_sizes_data_002(self):
        with Nd2(self.files[1]) as reader:
            self.assertEqual(reader.width, 512)
            self.assertEqual(reader.height, 256)
            self.assertEqual(len(reader.frames), 78)
            self.assertEqual(len(reader.channels), 1)
            self.assertEqual(len(reader.z_levels), 1)

    def test_frame_size_data_002(self):
        with Nd2(self.files[1]) as reader:
            frame = reader[13]
            self.assertEqual(frame.shape[1], 512)
            self.assertEqual(frame.shape[0], 256)
