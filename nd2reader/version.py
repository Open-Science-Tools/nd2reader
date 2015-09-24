import re


class InvalidVersionError(Exception):
    pass


def get_version(filename):
    """
    Determines what version the ND2 is.

    :param filename:    the path (absolute or relative) to the ND2
    :type filename:     str

    """
    with open(filename, 'rb') as f:
        # the first 16 bytes seem to have no meaning, so we skip them
        f.seek(16)
        # the next 38 bytes contain the string that we want to parse. Unlike most of the ND2, this is in UTF-8
        data = f.read(38).decode("utf8")
    return parse_version(data)


def parse_version(data):
    """
    Parses a string with the version data in it.

    :param data:    the 19th through 54th byte of the ND2, representing the version
    :type data:     unicode

    """
    match = re.search(r"""^ND2 FILE SIGNATURE CHUNK NAME01!Ver(?P<major>\d)\.(?P<minor>\d)$""", data)
    if match:
        # We haven't seen a lot of ND2s but the ones we have seen conform to this
        return int(match.group('major')), int(match.group('minor'))
    raise InvalidVersionError("The version of the ND2 you specified is not supported.")
