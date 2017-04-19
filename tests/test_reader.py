import unittest
from os import path
import numpy as np

from nd2reader.artificial import ArtificialND2
from nd2reader.common import check_or_make_dir
from nd2reader.exceptions import EmptyFileError
from nd2reader.parser import Parser
from nd2reader.reader import ND2Reader


class TestReader(unittest.TestCase):
    def test_extension(self):
        self.assertTrue('nd2' in ND2Reader.class_exts())
