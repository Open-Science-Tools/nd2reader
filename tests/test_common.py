import unittest
from os import path

import array
import six
import struct

from nd2reader.artificial import ArtificialND2
from nd2reader.common import get_version, parse_version, parse_date, _add_to_metadata, _parse_unsigned_char, \
    _parse_unsigned_int, _parse_unsigned_long, _parse_double, check_or_make_dir, _parse_string, _parse_char_array, \
    get_from_dict_if_exists
from nd2reader.exceptions import InvalidVersionError


class TestCommon(unittest.TestCase):
    def setUp(self):
        dir_path = path.dirname(path.realpath(__file__))
        check_or_make_dir(path.join(dir_path, 'test_data/'))
        self.test_file = path.join(dir_path, 'test_data/test.nd2')

    def create_test_nd2(self):
        with ArtificialND2(self.test_file) as artificial:
            artificial.close()

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

    def test_parse_version_invalid(self):
        data = 'ND2 FILE SIGNATURE CHUNK NAME!Version2.2.3'
        self.assertRaises(InvalidVersionError, parse_version, data)

    def test_get_version_from_file(self):
        self.create_test_nd2()

        with open(self.test_file, 'rb') as fh:
            version_tuple = get_version(fh)
            self.assertTupleEqual(version_tuple, (3, 0))

    def test_parse_date_24(self):
        date_format = "%m/%d/%Y  %H:%M:%S"
        date = '02/13/2016  23:43:37'
        textinfo = {six.b('TextInfoItem9'): six.b(date)}
        result = parse_date(textinfo)
        self.assertEqual(result.strftime(date_format), date)

    def test_parse_date_12(self):
        date_format = "%m/%d/%Y  %I:%M:%S %p"
        date = '02/13/2016  11:43:37 PM'
        textinfo = {six.b('TextInfoItem9'): six.b(date)}
        result = parse_date(textinfo)
        self.assertEqual(result.strftime(date_format), date)

    def test_parse_date_exception(self):
        date = 'i am no date'
        textinfo = {six.b('TextInfoItem9'): six.b(date)}
        result = parse_date(textinfo)
        self.assertIsNone(result)

    def test_add_to_meta_simple(self):
        metadata = {}
        _add_to_metadata(metadata, 'test', 'value')
        self.assertDictEqual(metadata, {'test': 'value'})

    def test_add_to_meta_new_list(self):
        metadata = {'test': 'value1'}
        _add_to_metadata(metadata, 'test', 'value2')
        self.assertDictEqual(metadata, {'test': ['value1', 'value2']})

    def test_add_to_meta_existing_list(self):
        metadata = {'test': ['value1', 'value2']}
        _add_to_metadata(metadata, 'test', 'value3')
        self.assertDictEqual(metadata, {'test': ['value1', 'value2', 'value3']})

    @staticmethod
    def _prepare_bin_stream(binary_format, *value):
        file = six.BytesIO()
        data = struct.pack(binary_format, *value)
        file.write(data)
        file.seek(0)
        return file

    def test_parse_functions(self):
        file = self._prepare_bin_stream("B", 9)
        self.assertEqual(_parse_unsigned_char(file), 9)

        file = self._prepare_bin_stream("I", 333)
        self.assertEqual(_parse_unsigned_int(file), 333)

        file = self._prepare_bin_stream("Q", 7564332)
        self.assertEqual(_parse_unsigned_long(file), 7564332)

        file = self._prepare_bin_stream("d", 47.9)
        self.assertEqual(_parse_double(file), 47.9)

        test_string = 'colloid'
        file = self._prepare_bin_stream("%ds" % len(test_string), six.b(test_string))
        parsed = _parse_string(file)
        self.assertEqual(parsed, test_string)

        test_data = [1, 2, 3, 4, 5]
        file = self._prepare_bin_stream("Q" + ''.join(['B'] * len(test_data)), len(test_data), *test_data)
        parsed = _parse_char_array(file)
        self.assertEqual(parsed, array.array('B', test_data))

    def test_get_from_dict_if_exists(self):
        test_dict = {
            six.b('existing'): 'test',
            'string': 'test2'
        }

        self.assertIsNone(get_from_dict_if_exists('nowhere', test_dict))
        self.assertEqual(get_from_dict_if_exists('existing', test_dict), 'test')
        self.assertEqual(get_from_dict_if_exists('string', test_dict, convert_key_to_binary=False), 'test2')
