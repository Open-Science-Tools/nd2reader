from os import path
from nd2reader.reader import ND2Reader
from nd2reader.legacy import Nd2

#try:
import importlib.metadata as importlib_metadata
#except:
#    import importlib_metadata

try:
    __version__ = importlib_metadata.version(__name__)
except:
    raise ValueError('Unable to read version number')
