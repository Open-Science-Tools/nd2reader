import nd2reader
import unittest


class VersionTests(unittest.TestCase):
    def test_versions_in_sync(self):
        # just make sure the version number exists and is the type we expect
        self.assertEqual(type(nd2reader.__version__), str)
