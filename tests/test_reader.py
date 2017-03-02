import unittest
from os import path

from nd2reader.reader import ND2Reader


class TestReader(unittest.TestCase):

    def setUp(self):
        dir_path = path.dirname(path.realpath(__file__))
        self.files = [
            path.join(dir_path, 'test_data/data001.nd2'),
            path.join(dir_path, 'test_data/data002.nd2')
        ]

    def test_sizes_data_001(self):
        with ND2Reader(self.files[0]) as reader:
            self.assertEqual(reader.sizes['x'], 128)
            self.assertEqual(reader.sizes['y'], 128)
            self.assertEqual(reader.sizes['t'], 982)
            self.assertEqual(reader.sizes['c'], 1)
            self.assertEqual(reader.sizes['z'], 1)

    def test_frame_size_data_001(self):
        with ND2Reader(self.files[0]) as reader:
            frame = reader[13]
            self.assertEqual(frame.shape[0], 128)
            self.assertEqual(frame.shape[1], 128)

    def test_sizes_data_002(self):
        with ND2Reader(self.files[1]) as reader:
            self.assertEqual(reader.sizes['x'], 512)
            self.assertEqual(reader.sizes['y'], 256)
            self.assertEqual(reader.sizes['t'], 78)
            self.assertEqual(reader.sizes['c'], 1)
            self.assertEqual(reader.sizes['z'], 1)

    def test_frame_size_data_002(self):
        with ND2Reader(self.files[1]) as reader:
            frame = reader[13]
            self.assertEqual(frame.shape[1], 512)
            self.assertEqual(frame.shape[0], 256)


