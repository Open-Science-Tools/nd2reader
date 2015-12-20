import struct
import array
import six


def read_chunk(fh, chunk_location):
    """
    Reads a piece of data given the location of its pointer.

    :param fh:    an open file handle to the ND2
    :param chunk_location:    a pointer
    :type chunk_location:    int

    :rtype: bytes

    """
    if chunk_location is None:
        return None
    fh.seek(chunk_location)
    # The chunk metadata is always 16 bytes long
    chunk_metadata = fh.read(16)
    header, relative_offset, data_length = struct.unpack("IIQ", chunk_metadata)
    if header != 0xabeceda:
        raise ValueError("The ND2 file seems to be corrupted.")
    # We start at the location of the chunk metadata, skip over the metadata, and then proceed to the
    # start of the actual data field, which is at some arbitrary place after the metadata.
    fh.seek(chunk_location + 16 + relative_offset)
    return fh.read(data_length)


def read_array(fh, kind, chunk_location):
    kinds = {'double': 'd',
             'int': 'i',
             'float': 'f'}
    if kind not in kinds:
        raise ValueError('You attempted to read an array of an unknown type.')
    raw_data = read_chunk(fh, chunk_location)
    if raw_data is None:
        return None
    return array.array(kinds[kind], raw_data)


def _parse_unsigned_char(data):
    return struct.unpack("B", data.read(1))[0]


def _parse_unsigned_int(data):
    return struct.unpack("I", data.read(4))[0]


def _parse_unsigned_long(data):
    return struct.unpack("Q", data.read(8))[0]


def _parse_double(data):
    return struct.unpack("d", data.read(8))[0]


def _parse_string(data):
    value = data.read(2)
    while not value.endswith(six.b("\x00\x00")):
        # the string ends at the first instance of \x00\x00
        value += data.read(2)
    return value.decode("utf16")[:-1].encode("utf8")


def _parse_char_array(data):
    array_length = struct.unpack("Q", data.read(8))[0]
    return array.array("B", data.read(array_length))


def _parse_metadata_item(data, cursor_position):
    """
    Reads hierarchical data, analogous to a Python dict.

    """
    new_count, length = struct.unpack("<IQ", data.read(12))
    length -= data.tell() - cursor_position
    next_data_length = data.read(length)
    value = read_metadata(next_data_length, new_count)
    # Skip some offsets
    data.read(new_count * 8)
    return value


def _get_value(data, data_type, cursor_position):
    """
    ND2s use various codes to indicate different data types, which we translate here.

    """
    parser = {1: _parse_unsigned_char,
              2: _parse_unsigned_int,
              3: _parse_unsigned_int,
              5: _parse_unsigned_long,
              6: _parse_double,
              8: _parse_string,
              9: _parse_char_array,
              11: _parse_metadata_item}
    return parser[data_type](data) if data_type < 11 else parser[data_type](data, cursor_position)


def read_metadata(data, count):
    """
    Iterates over each element some section of the metadata and parses it.

    """
    if data is None:
        return None
    data = six.BytesIO(data)
    metadata = {}
    for _ in range(count):
        cursor_position = data.tell()
        header = data.read(2)
        if not header:
            # We've reached the end of some hierarchy of data
            break
        if six.PY3:
            header = header.decode("utf8")
        data_type, name_length = map(ord, header)
        name = data.read(name_length * 2).decode("utf16")[:-1].encode("utf8")
        value = _get_value(data, data_type, cursor_position)
        if name not in metadata.keys():
            metadata[name] = value
        else:
            if not isinstance(metadata[name], list):
                # We have encountered this key exactly once before. Since we're seeing it again, we know we
                # need to convert it to a list before proceeding.
                metadata[name] = [metadata[name]]
            # We've encountered this key before so we're guaranteed to be dealing with a list. Thus we append
            # the value to the already-existing list.
            metadata[name].append(value)
    return metadata
