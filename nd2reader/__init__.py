import logging
from nd2reader.service import BaseNd2

log = logging.getLogger("nd2reader")
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)


class Nd2(BaseNd2):
    def __init__(self, filename):
        super(Nd2, self).__init__(filename)