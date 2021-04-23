# -*- coding: utf-8 -*-
import numpy as np  # type: ignore
import warnings


def get_unwanted_bytes_ids(image_group_data, image_data_start, height, width):
    # Check if the byte array size conforms to the image axes size. If not, check
    # that the number of unexpected (unwanted) bytes is a multiple of the number of
    # rows (height), as the same unmber of unwanted bytes is expected to be
    # appended at the end of each row. Then, returns the indexes of the unwanted
    # bytes.
    # Skip the first 4 elements that correspond to the time stamp
    number_of_true_channels = int(len(image_group_data[4:]) / (height * width))
    n_unwanted_bytes = (len(image_group_data[4:])) % (height * width)
    if not n_unwanted_bytes:
        return np.arange(0)
    assert 0 == n_unwanted_bytes % height, (
        "An unexpected number of extra bytes was encountered based on the expected"
        + " frame size, therefore the file could not be parsed."
    )
    return np.arange(
        image_data_start + height * number_of_true_channels,
        len(image_group_data) - n_unwanted_bytes + 1,
        height * number_of_true_channels,
    )


def remove_bytes_by_id(byte_ids, image_group_data, height):
    # Remove bytes by ID.
    bytes_per_row = len(byte_ids) // height
    warnings.warn(
        f"{len(byte_ids)} ({bytes_per_row}*{height}) unexpected zero "
        + "bytes were found in the ND2 file and removed to allow further parsing."
    )
    for i in range(len(byte_ids)):
        del image_group_data[byte_ids[i] : (byte_ids[i] + bytes_per_row)]


def remove_parsed_unwanted_bytes(image_group_data, image_data_start, height, width):
    # Stitched ND2 files have been reported to contain unexpected (according to
    # image shape) zero bytes at the end of each image data row. This hinders
    # proper reshaping of the data. Hence, here the unwanted zero bytes are
    # identified and removed.
    unwanted_byte_ids = get_unwanted_bytes_ids(
        image_group_data, image_data_start, height, width
    )
    if 0 != len(unwanted_byte_ids):
        assert np.all(
            image_group_data[unwanted_byte_ids + np.arange(len(unwanted_byte_ids))] == 0
        ), (
            f"{len(unwanted_byte_ids)} unexpected non-zero bytes were found"
            + " in the ND2 file, the file could not be parsed."
        )
        remove_bytes_by_id(unwanted_byte_ids, image_group_data, height)
    return image_group_data
