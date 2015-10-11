"""
These tests require that you have a specific ND2 file created by the developer of nd2reader. You will never need to
run them unless you're Jim Rybarski.

"""
from nd2reader import Nd2
from datetime import datetime
import unittest


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        self.nd2 = Nd2("FYLM-141111-001.nd2")

    def tearDown(self):
        self.nd2.close()

    def test_shape(self):
        self.assertEqual(self.nd2.height, 1280)
        self.assertEqual(self.nd2.width, 800)

    def test_date(self):
        self.assertEqual(self.nd2.date, datetime(2014, 11, 11, 15, 59, 19))

    def test_length(self):
        self.assertEqual(len(self.nd2), 30528)

    def test_frames(self):
        self.assertEqual(len(self.nd2.frames), 636)

    def test_fovs(self):
        self.assertEqual(len(self.nd2.fields_of_view), 8)

    def test_channels(self):
        self.assertTupleEqual(tuple(sorted(self.nd2.channels)), ('', 'GFP'))

    def test_z_levels(self):
        self.assertTupleEqual(tuple(self.nd2.z_levels), (0, 1, 2))

    def test_image(self):
        image = self.nd2[14]
        self.assertEqual(image.field_of_view, 2)
        self.assertEqual(image.frame_number, 0)
        self.assertAlmostEqual(image.timestamp, 19.0340758)
        self.assertEqual(image.channel, '')
        self.assertEqual(image.z_level, 1)
        self.assertEqual(image.height, self.nd2.height)
        self.assertEqual(image.width, self.nd2.width)

    def test_last_image(self):
        image = self.nd2[30526]
        self.assertEqual(image.frame_number, 635)

    def test_bad_image(self):
        image = self.nd2[13]
        self.assertIsNone(image)

    def test_iteration(self):
        images = [image for image in self.nd2[:10]]
        self.assertEqual(len(images), 10)

    def test_iteration_step(self):
        images = [image for image in self.nd2[:10:2]]
        self.assertEqual(len(images), 5)

    def test_iteration_backwards(self):
        images = [image for image in self.nd2[:10:-1]]
        self.assertEqual(len(images), 10)
