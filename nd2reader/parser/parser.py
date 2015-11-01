from nd2reader.parser.v3 import V3Parser
from nd2reader.exc import InvalidVersionError


def get_parser(fh, major_version, minor_version):
    """
    Picks the appropriate parser based on the ND2 version.

    :type fh:    file
    :type major_version:    int
    :type minor_version:    int

    :rtype:    a parser object

    """
    parsers = {(3, None): V3Parser}
    parser = parsers.get((major_version, minor_version)) or parsers.get((major_version, None))
    if not parser:
        raise InvalidVersionError("No parser is available for that version.")
    return parser(fh)
