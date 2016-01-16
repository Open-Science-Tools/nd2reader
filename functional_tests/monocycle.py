"""
Tests on ND2s that have 1 or 2 cycles only. This is unlike the ND2s I work with typically, which are all done over very long periods of time.

"""
from nd2reader import Nd2
import numpy as np
import unittest


class Monocycle1Tests(unittest.TestCase):
    def setUp(self):
        self.nd2 = Nd2("/var/nd2s/simone1.nd2")

    def tearDown(self):
        self.nd2.close()

    def test_channels(self):
        self.assertListEqual(self.nd2.channels, ['Cy3Narrow', 'TxRed-modified', 'FITC', 'DAPI'])

    def test_pixel_size(self):
        self.assertGreater(self.nd2.pixel_microns, 0.0)

    def test_select(self):
        manual_images = []
        for _, image in zip(range(20), self.nd2):
            if image is not None and image.channel == 'FITC':
                manual_images.append(image)

        filter_images = []
        for image in self.nd2.select(channels='FITC'):
            filter_images.append(image)
            if len(filter_images) == len(manual_images):
                break

        self.assertEqual(len(manual_images), len(filter_images))
        self.assertGreater(len(manual_images), 0)
        for a, b in zip(manual_images, filter_images):
            self.assertTrue(np.array_equal(a, b))
            self.assertEqual(a.index, b.index)
            self.assertEqual(a.field_of_view, b.field_of_view)
            self.assertEqual(a.channel, b.channel)

    def test_select_order_all(self):
        # If we select every possible image using select(), we should just get every image in order
        n = 0
        for image in self.nd2.select(channels=['Cy3Narrow', 'DAPI', 'FITC', 'TxRed-modified'],
                                     z_levels=list(range(35)),
                                     fields_of_view=list(range(5))):
            while True:
                indexed_image = self.nd2[n]
                if indexed_image is not None:
                    break
                n += 1
            self.assertTrue(np.array_equal(image, indexed_image))
            n += 1
            if n > 100:
                # Quit after the first hundred images just to save time.
                # If there's a problem, we'll have seen it by now.
                break

    def test_select_order_subset(self):
        # Test that images are always yielded in increasing order. This guarantees that no matter what subset of images
        # we're filtering, we still get them in the chronological order they were acquired
        n = -1
        for image in self.nd2.select(channels='FITC',
                                     z_levels=[0, 1],
                                     fields_of_view=[1, 2, 4]):
            self.assertGreater(image.index, n)
            self.assertEqual(image.channel, 'FITC')
            self.assertIn(image.field_of_view, (1, 2, 4))
            self.assertIn(image.z_level, (0, 1))
            n = image.index
            if n > 100:
                break


class Monocycle2Tests(unittest.TestCase):
    def setUp(self):
        self.nd2 = Nd2("/var/nd2s/hawkjo.nd2")

    def tearDown(self):
        self.nd2.close()

    def test_pixel_size(self):
        self.assertGreater(round(self.nd2.pixel_microns, 2), 0.26)

    def test_select(self):
        manual_images = []
        for _, image in zip(range(20), self.nd2):
            if image is not None and image.channel == 'HHQ 500 LP 1':
                manual_images.append(image)

        filter_images = []
        for image in self.nd2.select(channels='HHQ 500 LP 1'):
            filter_images.append(image)
            if len(filter_images) == len(manual_images):
                break

        self.assertEqual(len(manual_images), len(filter_images))
        self.assertGreater(len(manual_images), 0)
        for a, b in zip(manual_images, filter_images):
            self.assertTrue(np.array_equal(a, b))
            self.assertEqual(a.index, b.index)
            self.assertEqual(a.field_of_view, b.field_of_view)
            self.assertEqual(a.channel, b.channel)

    def test_select_order_all(self):
        # If we select every possible image using select(), we should just get every image in order
        n = 0
        for image in self.nd2.select(channels=['HHQ 500 LP 1', 'HHQ 500 LP 2'],
                                     z_levels=[0],
                                     fields_of_view=list(range(100))):
            while True:
                indexed_image = self.nd2[n]
                if indexed_image is not None:
                    break
                n += 1
            self.assertTrue(np.array_equal(image, indexed_image))
            n += 1
            if n > 100:
                # Quit after the first hundred images just to save time.
                # If there's a problem, we'll have seen it by now.
                break

    def test_select_order_subset(self):
        # Test that images are always yielded in increasing order. This guarantees that no matter what subset of images
        # we're filtering, we still get them in the chronological order they were acquired
        n = -1
        for image in self.nd2.select(channels='HHQ 500 LP 2',
                                     z_levels=[0],
                                     fields_of_view=[1, 2, 4]):
            self.assertGreater(image.index, n)
            self.assertEqual(image.channel, 'HHQ 500 LP 2')
            self.assertIn(image.field_of_view, (1, 2, 4))
            self.assertEqual(image.z_level, 0)
            n = image.index
            if n > 100:
                break
