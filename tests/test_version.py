import unittest
from nd2reader import __version__ as VERSION


class TestVersion(unittest.TestCase):
    def test_module_version_type(self):
        # just make sure the version number exists and is the type we expect
        self.assertEqual(type(VERSION), str)
