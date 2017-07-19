import unittest
from os import path
from nd2reader.artificial import ArtificialND2
from nd2reader.common import check_or_make_dir
from nd2reader.exceptions import InvalidVersionError
from nd2reader.parser import Parser


class TestParser(unittest.TestCase):
    def create_test_nd2(self):
        with ArtificialND2(self.test_file) as artificial:
            artificial.close()

    def setUp(self):
        dir_path = path.dirname(path.realpath(__file__))
        check_or_make_dir(path.join(dir_path, 'test_data/'))
        self.test_file = path.join(dir_path, 'test_data/test.nd2')
        self.create_test_nd2()

    def test_can_open_test_file(self):
        self.create_test_nd2()

        with open(self.test_file, 'rb') as fh:
            parser = Parser(fh)
            self.assertTrue(parser.supported)

    def test_cannot_open_wrong_version(self):
        with ArtificialND2(self.test_file, version=('0', '0')) as _:
            with open(self.test_file, 'rb') as fh:
                with self.assertRaises(InvalidVersionError) as exception:
                    Parser(fh)
            self.assertEqual(str(exception.exception), "No parser is available for that version.")
