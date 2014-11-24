import numpy as np
import skimage.io
import logging

log = logging.getLogger("nd2reader")


class Channel(object):
    def __init__(self, name, camera, exposure_time):
        self._name = name
        self._camera = camera
        self._exposure_time = exposure_time

    @property
    def name(self):
        return self._name

    @property
    def camera(self):
        return self._camera

    @property
    def exposure_time(self):
        return self._exposure_time


class ImageSet(object):
    """
    A group of images that share the same timestamp. NIS Elements doesn't store a unique timestamp for every
    image, rather, it stores one for each set of images that share the same field of view and z-axis level.

    """
    def __init__(self):
        self._images = []

    def add(self, image):
        """
        :type image:    nd2reader.model.Image()

        """
        self._images.append(image)

    def __iter__(self):
        for image in self._images:
            yield image


class Image(object):
    def __init__(self, timestamp, raw_array, field_of_view, channel, z_level, height, width):
        self._timestamp = timestamp
        self._raw_data = raw_array
        self._field_of_view = field_of_view
        self._channel = channel
        self._z_level = z_level
        self._height = height
        self._width = width
        self._data = None

    @property
    def timestamp(self):
        # TODO: Convert to datetime object
        return self._timestamp / 1000.0

    @property
    def data(self):
        if self._data is None:
            self._data = np.reshape(self._raw_data, (self._height, self._width))
        return self._data

    @property
    def is_valid(self):
        return np.any(self.data)

    def show(self):
        skimage.io.imshow(self.data)
        skimage.io.show()


from io import BytesIO
import array
import struct


class Chunkmap(object):
    def __init__(self):
        pass

    def read(self, filename):
        with open(filename, "rb") as f:
            data = f.read(-1)
        self.parse(data, 1)

    def parse(self, data, count):
        data = BytesIO(data)
        res = {}
        total_count = 0
        for c in range(count):
            lastpos = data.tell()
            total_count += 1
            hdr = data.read(2)
            if not hdr:
                break
            typ = ord(hdr[0])
            bname = data.read(2*ord(hdr[1]))
            name = bname.decode("utf16")[:-1].encode("utf8")
            if typ == 1:
                value, = struct.unpack("B", data.read(1))
            elif typ in [2, 3]:
                value, = struct.unpack("I", data.read(4))
            elif typ == 5:
                value, = struct.unpack("Q", data.read(8))
            elif typ == 6:
                value, = struct.unpack("d", data.read(8))
            elif typ == 8:
                value = data.read(2)
                while value[-2:] != "\x00\x00":
                    value += data.read(2)
                value = value.decode("utf16")[:-1].encode("utf8")
            elif typ == 9:
                cnt, = struct.unpack("Q", data.read(8))
                value = array.array("B", data.read(cnt))
            elif typ == 11:
                curpos = data.tell()
                newcount, length = struct.unpack("<IQ", data.read(12))
                curpos = data.tell()
                length -= data.tell()-lastpos
                nextdata = data.read(length)
                value = self.parse(nextdata, newcount)
                print("WE GOT A NEW DICT")
                # Skip some offsets
                data.read(newcount * 8)
            else:
                assert 0, "%s hdr %x:%x unknown" % (name, ord(hdr[0]),  ord(hdr[1]))
            if not name in res:
                res[name] = value
            else:
                if not isinstance(res[name], list):
                    res[name] = [res[name]]
                res[name].append(value)
        x = data.read()
        assert not x, "skip %d %s" % (len(x), repr(x[:30]))
        return res