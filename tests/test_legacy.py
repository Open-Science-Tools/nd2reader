import unittest
import warnings

from nd2reader.legacy import Nd2
from nd2reader.reader import ND2Reader
from nd2reader.artificial import ArtificialND2


class TestLegacy(unittest.TestCase):
    def test_init(self):
        with ArtificialND2('test_data/legacy.nd2'):
            with warnings.catch_warnings(record=True) as w:
                # Cause all warnings to always be triggered.
                warnings.simplefilter("always")
                with Nd2('test_data/legacy.nd2') as reader:
                    self.assertIsInstance(reader.reader, ND2Reader)
                self.assertTrue(issubclass(w[0].category, DeprecationWarning))
                self.assertEquals(str(w[0].message), "The 'Nd2' class is deprecated, please consider using the new" +
                                  " ND2Reader interface which uses pims.")

    def test_misc(self):
        with ArtificialND2('test_data/legacy.nd2'):
            with Nd2('test_data/legacy.nd2') as reader:
                representation = "\n".join(["<Deprecated ND2 %s>" % reader.reader.filename,
                                            "Created: Unknown",
                                            "Image size: %sx%s (HxW)" % (reader.height, reader.width),
                                            "Frames: %s" % len(reader.frames),
                                            "Channels: %s" % ", ".join(["%s" % str(channel) for channel
                                                                        in reader.channels]),
                                            "Fields of View: %s" % len(reader.fields_of_view),
                                            "Z-Levels: %s" % len(reader.z_levels)
                                            ])
                self.assertEquals(representation, str(reader))

                # not implemented yet
                self.assertEquals(reader.pixel_microns, None)

                self.assertEquals(len(reader), 1)
