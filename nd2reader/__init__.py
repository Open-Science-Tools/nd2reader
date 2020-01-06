from os import path
from nd2reader.reader import ND2Reader
from nd2reader.legacy import Nd2

VERSION = ''
CURRENT_DIRECTORY = path.abspath(path.dirname(__file__))
with open(path.join(CURRENT_DIRECTORY, '..', 'VERSION')) as version_file:
    VERSION = version_file.read().strip()

__version__ = VERSION
