from nd2reader.parser.v3 import V3Parser
from nd2reader.exc import InvalidVersionError


def get_parser(filename, major_version, minor_version):
    parsers = {(3, None): V3Parser}
    parser = parsers.get((major_version, minor_version)) or parsers.get((major_version, None))
    if not parser:
        raise InvalidVersionError("No parser is available for that version.")
    return parser(filename)
