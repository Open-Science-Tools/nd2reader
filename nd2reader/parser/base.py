from abc import abstractproperty


class BaseParser(object):
    def __init__(self, fh):
        self._fh = fh
        self.camera_metadata = None
        self.metadata = None

    @abstractproperty
    def driver(self):
        """
        Must return an object that can look up and read images.

        """
        raise NotImplementedError
