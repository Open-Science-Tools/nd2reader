import array
import numpy as np
import struct
from collections import namedtuple
from StringIO import StringIO

chunk = namedtuple('Chunk', ['location', 'length'])
field_of_view = namedtuple('FOV', ['number', 'x', 'y', 'z', 'pfs_offset'])
channel = namedtuple('Channel', ['name', 'camera', 'exposure_time'])


class Nd2(object):
    def __init__(self, filename):
        self._parser = Nd2Parser(filename)

    @property
    def height(self):
        return self._parser.metadata['ImageAttributes']['SLxImageAttributes']['uiHeight']

    @property
    def width(self):
        return self._parser.metadata['ImageAttributes']['SLxImageAttributes']['uiWidth']

    @property
    def fields_of_view(self):
        for number, fov in enumerate(self.metadata['ImageMetadata']['SLxExperiment']['ppNextLevelEx']['']['uLoopPars']['Points']['']):
            yield field_of_view(number=number + 1, x=fov['dPosX'], y=fov['dPosY'], z=fov['dPosZ'], pfs_offset=fov['dPFSOffset'])

    @property
    def fov_count(self):
        return len(list(self.fields_of_view))

    @property
    def channels(self):
        metadata = self.metadata['ImageMetadataSeq']['SLxPictureMetadata']['sPicturePlanes']
        for label, chan in metadata['sPlaneNew'].items():
            name = chan['sDescription']
            exposure_time = metadata['sSampleSetting'][label]['dExposureTime']
            camera = metadata['sSampleSetting'][label]['pCameraSetting']['CameraUserName']
            yield channel(name=name, exposure_time=exposure_time, camera=camera)

    @property
    def metadata(self):
        return self._parser.metadata

    def get_images(self, fov_number, channel_name, z_axis):
        pass

    def get_image(self, nr):
        d = self._parser._read_chunk(self._parser._label_map["ImageDataSeq|%d!" % nr].location)
        acqtime = struct.unpack("d", d[:8])[0]
        res = [acqtime]
        for i in range(self.metadata['ImageAttributes']["SLxImageAttributes"]["uiComp"]):
            a = array.array("H", d)
            res.append(a[4+i::self.metadata['ImageAttributes']["SLxImageAttributes"]["uiComp"]])
        return res


class Nd2Parser(object):
    """
    Reads .nd2 files, provides an interface to the metadata, and generates numpy arrays from the image data.

    """
    def __init__(self, filename):
        self._filename = filename
        self._file_handler = None
        self._chunk_map_start_location = None
        self._label_map = {}
        self._metadata = {}
        self._read_map()
        self._parse_dict_data()

    @property
    def fh(self):
        if self._file_handler is None:
            self._file_handler = open(self._filename, "rb")
        return self._file_handler

    def _parse_dict_data(self):
        # TODO: Don't like this name
        for label in self._top_level_dict_labels:
            chunk_location = self._label_map[label].location
            data = self._read_chunk(chunk_location)
            stop = label.index("LV")
            self._metadata[label[:stop]] = self.read_lv_encoding(data, 1)

    @property
    def metadata(self):
        return self._metadata

    @property
    def _top_level_dict_labels(self):
        # TODO: I don't like this name either
        for label in self._label_map.keys():
            if label.endswith("LV!") or "LV|" in label:
                yield label

    def _read_map(self):
        """
        Every label ends with an exclamation point, however, we can't directly search for those to find all the labels
        as some of the bytes contain the value 33, which is the ASCII code for "!". So we iteratively find each label,
        grab the subsequent data (always 16 bytes long), advance to the next label and repeat.

        """
        raw_text = self._get_raw_chunk_map_text()
        label_start = self._find_first_label_offset(raw_text)
        while True:
            data_start = self._get_data_start(label_start, raw_text)
            label, value = self._extract_map_key(label_start, data_start, raw_text)
            if label == "ND2 CHUNK MAP SIGNATURE 0000001!":
                # We've reached the end of the chunk map
                break

            self._label_map[label] = value
            label_start = data_start + 16

    @staticmethod
    def _find_first_label_offset(raw_text):
        """
        The chunk map starts with some number of (seemingly) useless bytes, followed
        by "ND2 FILEMAP SIGNATURE NAME 0001!". We return the location of the first character after this sequence,
        which is the actual beginning of the chunk map.

        """
        return raw_text.index("ND2 FILEMAP SIGNATURE NAME 0001!") + 32

    @staticmethod
    def _get_data_start(label_start, raw_text):
        """
        The data for a given label begins immediately after the first exclamation point

        """
        return raw_text.index("!", label_start) + 1

    @staticmethod
    def _extract_map_key(label_start, data_start, raw_text):
        """
        Chunk map entries are a string label of arbitrary length followed by 16 bytes of data, which represent
        the byte offset from the beginning of the file where that data can be found.

        """
        key = raw_text[label_start: data_start]
        location, length = struct.unpack("QQ", raw_text[data_start: data_start + 16])
        return key, chunk(location=location, length=length)

    @property
    def chunk_map_start_location(self):
        """
        The position in bytes from the beginning of the file where the chunk map begins.
        The chunk map is a series of string labels followed by the position (in bytes) of the respective data.

        """
        if self._chunk_map_start_location is None:
            # Put the cursor 8 bytes before the end of the file
            self.fh.seek(-8, 2)
            # Read the last 8 bytes of the file
            self._chunk_map_start_location = struct.unpack("Q", self.fh.read(8))[0]
        return self._chunk_map_start_location

    def _read_chunk(self, chunk_location):
        """
        Gets the data for a given chunk pointer

        """
        self.fh.seek(chunk_location)
        chunk_data = self._read_chunk_metadata()
        header, relative_offset, data_length = self._parse_chunk_metadata(chunk_data)
        return self._read_chunk_data(chunk_location, relative_offset, data_length)

    def _read_chunk_metadata(self):
        """
        Gets the chunks metadata, which is always 16 bytes

        """
        return self.fh.read(16)

    def _read_chunk_data(self, chunk_location, relative_offset, data_length):
        """
        Reads the actual data for a given chunk

        """
        # We start at the location of the chunk metadata, skip over the metadata, and then proceed to the
        # start of the actual data field, which is at some arbitrary place after the metadata.
        self.fh.seek(chunk_location + 16 + relative_offset)
        return self.fh.read(data_length)

    @staticmethod
    def _parse_chunk_metadata(chunk_data):
        """
        Finds out everything about a given chunk. Every chunk begins with the same value, so if that's ever
        different we can assume the file has suffered some kind of damage.

        """
        header, relative_offset, data_length = struct.unpack("IIQ", chunk_data)
        if header != 0xabeceda:
            raise ValueError("The ND2 file seems to be corrupted.")
        return header, relative_offset, data_length

    def _get_raw_chunk_map_text(self):
        """
        Reads the entire chunk map and returns it as a string.

        """
        self.fh.seek(self.chunk_map_start_location)
        return self.fh.read(-1)

    @staticmethod
    def as_numpy_array(arr):
        return np.frombuffer(arr)

    def read_lv_encoding(self, data, count):
        data = StringIO(data)
        res = {}
        for c in range(count):
            lastpos = data.tell()
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
                newcount, length = struct.unpack("<IQ", data.read(12))
                length -= data.tell()-lastpos
                nextdata = data.read(length)
                value = self.read_lv_encoding(nextdata, newcount)
                # XXX do not know for what these offsets? are
                unknown = array.array("I", data.read(newcount*8))
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

#
# class LVLine(object):
#     def __init__(self, line):
#         self._line = line
#         self._extract()
#
#     def _extract(self):
#         if self._type == 11:
#             count, length = struct.unpack("<IQ", self._line[self._name_end: self._name_end + 12])
#             newline = self._line[self._name_end + 12:]
#
#     @property
#     def name(self):
#         return self._line[2: self._name_end].decode("utf16").encode("utf8")
#
#     @property
#     def _type(self):
#         return ord(self._line[0])
#
#     @property
#     def _name_end(self):
#         """
#         Length is given as number of characters, but since it's unicode (which is two-bytes per character) we return
#         twice the number.
#
#         """
#         return ord(self._line[1]) * 2
#
#
# class LVData(object):
#     def __init__(self, data):
#         self._extracted_data = LVLine(data)