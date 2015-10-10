import unittest
from nd2reader.version import parse_version


class VersionTests(unittest.TestCase):
    def test_parse_version_2(self):
        data = 'ND2 FILE SIGNATURE CHUNK NAME01!Ver2.2'
        actual = parse_version(data)
        expected = (2, 2)
        self.assertTupleEqual(actual, expected)

    def test_parse_version_3(self):
        data = 'ND2 FILE SIGNATURE CHUNK NAME01!Ver3.0'
        actual = parse_version(data)
        expected = (3, 0)
        self.assertTupleEqual(actual, expected)
