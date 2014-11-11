class Channel(object):
    def __init__(self, name, camera, exposure_time):
        self._name = name
        self._camera = camera
        self._exposure_time = exposure_time

    @property
    def name(self):
        if self._name is not None and self._name != "":
            return self._name
        return "UnnamedChannel"

    @property
    def camera(self):
        return self._camera

    @property
    def exposure_time(self):
        return self._exposure_time


class Image(object):
    def __init__(self):
        self.timestamp = None