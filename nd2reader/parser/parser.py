from nd2reader.parser.v3 import V3Parser
import re
from nd2reader.exc import InvalidVersionError


def get_parser(fh):
    """
    Picks the appropriate parser based on the ND2 version.

    :type fh:    file
    :type major_version:    int
    :type minor_version:    int

    :rtype:    a parser object

    """
    major_version, minor_version = get_version(fh)
    parsers = {(3, None): V3Parser}
    parser = parsers.get((major_version, minor_version)) or parsers.get((major_version, None))
    if not parser:
        raise InvalidVersionError("No parser is available for that version.")
    return parser(fh)


def get_version(fh):
    """
    Determines what version the ND2 is.

    :param fh:    an open file handle to the ND2
    :type fh:     file

    """
    # the first 16 bytes seem to have no meaning, so we skip them
    fh.seek(16)

    # the next 38 bytes contain the string that we want to parse. Unlike most of the ND2, this is in UTF-8
    data = fh.read(38).decode("utf8")
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
