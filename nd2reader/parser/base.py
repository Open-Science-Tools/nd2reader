from abc import abstractproperty


class BaseParser(object):
    @abstractproperty
    def metadata(self):
        raise NotImplementedError

    @abstractproperty
    def driver(self):
        raise NotImplementedError
