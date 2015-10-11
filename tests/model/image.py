from nd2reader.model.image import Image
import numpy as np
import unittest


class ImageTests(unittest.TestCase):
    """
    Basically just tests that the Image API works and that Images act as Numpy arrays. There's very little going on
    here other than simply storing data.

    """
    def setUp(self):
        array = np.array([[0, 1, 254],
                          [45, 12, 9],
                          [12, 12, 99]])
        self.image = Image(array)
        self.image.add_params(1200.314, 17, 2, 'GFP', 1)

    def test_size(self):
        self.assertEqual(self.image.height, 3)
        self.assertEqual(self.image.width, 3)

    def test_timestamp(self):
        self.assertEqual(self.image.timestamp, 1.200314)

    def test_frame_number(self):
        self.assertEqual(self.image.frame_number, 17)

    def test_fov(self):
        self.assertEqual(self.image.field_of_view, 2)

    def test_channel(self):
        self.assertEqual(self.image.channel, 'GFP')

    def test_z_level(self):
        self.assertEqual(self.image.z_level, 1)

    def test_slice(self):
        subimage = self.image[:2, :2]
        expected = np.array([[0, 1],
                             [45, 12]])
        self.assertTrue(np.array_equal(subimage, expected))
