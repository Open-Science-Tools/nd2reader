import unittest
import numpy as np
import struct

from pims import Frame
from nd2reader.artificial import ArtificialND2
from nd2reader.exceptions import EmptyFileError
from nd2reader.reader import ND2Reader
from nd2reader.parser import Parser


class TestReader(unittest.TestCase):
    def test_extension(self):
        self.assertTrue('nd2' in ND2Reader.class_exts())

    def test_init_and_init_axes(self):
        with ArtificialND2('test_data/test_nd2_reader.nd2') as artificial:
            with ND2Reader('test_data/test_nd2_reader.nd2') as reader:
                attributes = artificial.data['image_attributes']['SLxImageAttributes']
                self.assertEqual(reader.metadata['width'], attributes['uiWidth'])
                self.assertEqual(reader.metadata['height'], attributes['uiHeight'])

                self.assertEqual(reader.metadata['width'], reader.sizes['x'])
                self.assertEqual(reader.metadata['height'], reader.sizes['y'])

                self.assertEqual(reader.pixel_type, np.float64)
                self.assertEqual(reader.iter_axes, ['t'])

    def test_init_empty_file(self):
        with ArtificialND2('test_data/empty.nd2', skip_blocks=['label_map_marker']):
            with self.assertRaises(EmptyFileError) as exception:
                with ND2Reader('test_data/empty.nd2'):
                    pass
            self.assertEqual(str(exception.exception), "No axes were found for this .nd2 file.")

    def test_get_parser(self):
        with ArtificialND2('test_data/test_nd2_reader.nd2') as _:
            with ND2Reader('test_data/test_nd2_reader.nd2') as reader:
                self.assertIsInstance(reader.parser, Parser)

    def test_get_timesteps(self):
        with ArtificialND2('test_data/test_nd2_reader.nd2') as _:
            with ND2Reader('test_data/test_nd2_reader.nd2') as reader:
                timesteps = reader.timesteps
                self.assertEquals(len(timesteps), 0)

    def test_get_frame_zero(self):
        # Best test we can do for now:
        # test everything up to the actual unpacking of the frame data
        with ArtificialND2('test_data/test_nd2_reader.nd2') as _:
            with ND2Reader('test_data/test_nd2_reader.nd2') as reader:

                with self.assertRaises(struct.error) as exception:
                    frame = reader[0]

                self.assertIn('unpack', str(exception.exception))

    def test_get_frame_2D(self):
        # Best test we can do for now:
        # test everything up to the actual unpacking of the frame data
        with ArtificialND2('test_data/test_nd2_reader.nd2') as _:
            with ND2Reader('test_data/test_nd2_reader.nd2') as reader:

                with self.assertRaises(struct.error) as exception:
                    frame = reader.get_frame_2D(c=0, t=0, z=0, x=0, y=0, v=0)

                self.assertIn('unpack', str(exception.exception))
