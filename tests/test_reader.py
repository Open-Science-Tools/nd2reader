import unittest
from os import path
import numpy as np

from nd2reader.artificial import ArtificialND2
from nd2reader.common import check_or_make_dir
from nd2reader.parser import Parser
from nd2reader.reader import ND2Reader


class TestReader(unittest.TestCase):
    def create_test_nd2(self):
        with ArtificialND2(self.test_file) as artificial:
            artificial.close()

    def setUp(self):
        dir_path = path.dirname(path.realpath(__file__))
        check_or_make_dir(path.join(dir_path, 'test_data/'))
        self.test_file = path.join(dir_path, 'test_data/test.nd2')

    def test_can_open_test_file(self):
        self.create_test_nd2()
        with ND2Reader(self.test_file) as reader:
            self.assertEqual(reader.filename, self.test_file)
            self.assertEqual(reader.pixel_type, np.float64)
            self.assertEqual(reader.sizes['x'], 0)
            self.assertEqual(reader.sizes['y'], 0)
            self.assertFalse('z' in reader.sizes)
            self.assertEqual(reader.sizes['c'], 0)
            self.assertEqual(reader.sizes['t'], 0)

    def test_extension(self):
        self.assertTrue('nd2' in ND2Reader.class_exts())

    def test_get_metadata_property(self):
        self.create_test_nd2()
        with ND2Reader(self.test_file) as reader:
            self.assertIsNone(reader._get_metadata_property('kljdf'))
            self.assertEqual(reader._get_metadata_property('kljdf', 'default'), 'default')

    def test_get_parser(self):
        self.create_test_nd2()
        with ND2Reader(self.test_file) as reader:
            self.assertTrue(type(reader.parser) is Parser)

