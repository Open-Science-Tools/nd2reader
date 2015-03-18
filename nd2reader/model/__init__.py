import numpy as np
import skimage.io
import logging
from io import BytesIO
import array
import struct


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
    def field_of_view(self):
        return self._field_of_view

    @property
    def timestamp(self):
        """
        The number of seconds after the beginning of the acquisition that the image was taken. Note that for a given field
        of view and z-level offset, if you have images of multiple channels, they will all be given the same timestamp.
        No, this doesn't make much sense. But that's how ND2s are structured, so if your experiment depends on millisecond
        accuracy, you need to find an alternative imaging system.

        """
        return self._timestamp / 1000.0

    @property
    def channel(self):
        return self._channel

    @property
    def z_level(self):
        return self._z_level

    @property
    def data(self):
        if self._data is None:
            # The data is just a flat, 1-dimensional array. We convert it to a 2D array and cast the data points as 16-bit integers
            self._data = np.reshape(self._raw_data, (self._height, self._width)).astype(np.int64).astype(np.uint16)
        return self._data

    @property
    def is_valid(self):
        return np.any(self.data)

    def show(self):
        skimage.io.imshow(self.data)
        skimage.io.show()


class MetadataItem(object):
    def __init__(self, start, data):
        self._datatype = ord(data[start])
        self._label_length = 2 * ord(data[start + 1])
        self._data = data

    @property
    def is_valid(self):
        return self._datatype > 0

    @property
    def key(self):
        return self._data[2:self._label_length].decode("utf16").encode("utf8")

    @property
    def length(self):
        return self._length

    @property
    def data_start(self):
        return self._label_length + 2

    @property
    def _body(self):
        """
        All data after the header.

        """
        return self._data[self.data_start:]

    def _get_bytes(self, count):
        return self._data[self.data_start: self.data_start + count]

    @property
    def value(self):
        parser = {1: self._parse_unsigned_char,
                  2: self._parse_unsigned_int,
                  3: self._parse_unsigned_int,
                  5: self._parse_unsigned_long,
                  6: self._parse_double,
                  8: self._parse_string,
                  9: self._parse_char_array,
                  11: self._parse_metadata_item
                  }
        return parser[self._datatype]()

    def _parse_unsigned_char(self):
        self._length = 1
        return self._unpack("B", self._get_bytes(self._length))

    def _parse_unsigned_int(self):
        self._length = 4
        return self._unpack("I", self._get_bytes(self._length))

    def _parse_unsigned_long(self):
        self._length = 8
        return self._unpack("Q", self._get_bytes(self._length))

    def _parse_double(self):
        self._length = 8
        return self._unpack("d", self._get_bytes(self._length))

    def _parse_string(self):
        # the string is of unknown length but ends at the first instance of \x00\x00
        stop = self._body.index("\x00\x00")
        self._length = stop
        return self._body[:stop - 1].decode("utf16").encode("utf8")

    def _parse_char_array(self):
        array_length = self._unpack("Q", self._get_bytes(8))
        self._length = array_length + 8
        return array.array("B", self._body[8:array_length])

    def _parse_metadata_item(self):
        count, length = struct.unpack("<IQ", self._get_bytes(12))
        metadata_set = MetadataSet(self._body, 0, count)

    def _unpack(self, kind, data):
        """
        :param kind:    the datatype to interpret the bytes as (see: https://docs.python.org/2/library/struct.html#struct-format-strings)
        :type kind:     str
        :param data:    the bytes to be converted
        :type data:     bytes

        Parses a sequence of bytes and converts them to a Python data type.
        struct.unpack() returns a tuple but we only want the first element.

        """
        return struct.unpack(kind, data)[0]


class MetadataSet(object):
    """
    A container of metadata items. Can contain other MetadataSet objects.

    """
    def __init__(self, data, start, item_count):
        self._items = []
        self._parse(data, start, item_count)

    def _parse(self, data, start, item_count):
        for item in range(item_count):
            metadata_item = MetadataItem(start, data)
            if not metadata_item.is_valid:
                break
            start += metadata_item.length


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