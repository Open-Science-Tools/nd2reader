import struct


def read_chunk(fh, chunk_location):
    """
    Gets the data for a given chunk pointer

    :rtype: bytes

    """
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
