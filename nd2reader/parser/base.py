from abc import abstractproperty


class BaseParser(object):
    @abstractproperty
    def metadata(self):
        """
        Instantiates a Metadata object.

        """
        raise NotImplementedError

    @abstractproperty
    def driver(self):
        """
        Instantiates a driver object.

        """
        raise NotImplementedError
