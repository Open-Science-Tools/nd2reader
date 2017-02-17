import nd2reader
import unittest
from setup import VERSION


class TestVersion(unittest.TestCase):
    def test_module_version_type(self):
        # just make sure the version number exists and is the type we expect
        self.assertEqual(type(nd2reader.__version__), str)

    def test_versions_in_sync(self):
        self.assertEqual(nd2reader.__version__, VERSION)
