"""
These tests require that you have a specific ND2 file created by the developer of nd2reader. You will never need to
run them unless you're Jim Rybarski.

"""
from nd2reader import Nd2
from datetime import datetime
import unittest


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        self.nd2 = Nd2("/var/nd2s/FYLM-141111-001.nd2")

    def tearDown(self):
        self.nd2.close()

    def test_shape(self):
        self.assertEqual(self.nd2.height, 1280)
        self.assertEqual(self.nd2.width, 800)

    def test_date(self):
        self.assertEqual(self.nd2.date, datetime(2014, 11, 11, 15, 59, 19))

    # def test_length(self):
    #     # This will fail until we address issue #59
    #     self.assertEqual(len(self.nd2), 17808)

    def test_frames(self):
        self.assertEqual(len(self.nd2.frames), 636)

    def test_fovs(self):
        self.assertEqual(len(self.nd2.fields_of_view), 8)

    def test_channels(self):
        self.assertTupleEqual(tuple(sorted(self.nd2.channels)), ('BF', 'GFP'))

    def test_z_levels(self):
        self.assertTupleEqual(tuple(self.nd2.z_levels), (0, 1, 2))

    def test_image(self):
        image = self.nd2[14]
        self.assertEqual(image.field_of_view, 2)
        self.assertEqual(image.frame_number, 0)
        self.assertAlmostEqual(image.timestamp, 19.0340758)
        self.assertEqual(image.channel, 'BF')
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

    def test_get_image_by_attribute_ok(self):
        image = self.nd2.get_image(4, 0, "GFP", 1)
        self.assertIsNotNone(image)
        image = self.nd2.get_image(4, 0, "BF", 0)
        self.assertIsNotNone(image)
        image = self.nd2.get_image(4, 0, "BF", 1)
        self.assertIsNotNone(image)

    def test_images(self):
        self.assertTupleEqual((self.nd2[0].z_level, self.nd2[0].channel), (0, 'BF'))
        self.assertIsNone(self.nd2[1])
        self.assertTupleEqual((self.nd2[2].z_level, self.nd2[2].channel), (1, 'BF'))
        self.assertTupleEqual((self.nd2[3].z_level, self.nd2[3].channel), (1, 'GFP'))
        self.assertTupleEqual((self.nd2[4].z_level, self.nd2[4].channel), (2, 'BF'))
        self.assertIsNone(self.nd2[5])
        self.assertTupleEqual((self.nd2[6].z_level, self.nd2[6].channel), (0, 'BF'))
        self.assertIsNone(self.nd2[7])
        self.assertTupleEqual((self.nd2[8].z_level, self.nd2[8].channel), (1, 'BF'))
        self.assertTupleEqual((self.nd2[9].z_level, self.nd2[9].channel), (1, 'GFP'))
        self.assertTupleEqual((self.nd2[10].z_level, self.nd2[10].channel), (2, 'BF'))
        self.assertIsNone(self.nd2[11])
        self.assertTupleEqual((self.nd2[12].z_level, self.nd2[12].channel), (0, 'BF'))
        self.assertIsNone(self.nd2[13])
        self.assertTupleEqual((self.nd2[14].z_level, self.nd2[14].channel), (1, 'BF'))
        self.assertTupleEqual((self.nd2[15].z_level, self.nd2[15].channel), (1, 'GFP'))
        self.assertTupleEqual((self.nd2[16].z_level, self.nd2[16].channel), (2, 'BF'))
        self.assertIsNone(self.nd2[17])
        self.assertTupleEqual((self.nd2[18].z_level, self.nd2[18].channel), (0, 'BF'))
        self.assertIsNone(self.nd2[19])
        self.assertIsNone(self.nd2[47])
        self.assertTupleEqual((self.nd2[48].z_level, self.nd2[48].channel), (0, 'BF'))
        self.assertIsNone(self.nd2[49])
        self.assertTupleEqual((self.nd2[50].z_level, self.nd2[50].channel), (1, 'BF'))
        self.assertIsNone(self.nd2[51])
        self.assertTupleEqual((self.nd2[52].z_level, self.nd2[52].channel), (2, 'BF'))
        self.assertIsNone(self.nd2[53])
        self.assertTupleEqual((self.nd2[54].z_level, self.nd2[54].channel), (0, 'BF'))

    def test_get_image_by_attribute_none(self):
        image = self.nd2.get_image(4, 0, "GFP", 0)
        self.assertIsNone(image)
