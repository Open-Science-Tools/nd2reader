import unittest

from nd2reader.reader import ND2Reader


class TestReader(unittest.TestCase):
    def test_extension(self):
        self.assertTrue('nd2' in ND2Reader.class_exts())
