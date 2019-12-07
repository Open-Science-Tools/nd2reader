class InvalidFileType(Exception):
    """Non .nd2 extension file.

    File does not have an extension .nd2.

    """
    pass

class InvalidVersionError(Exception):
    """Unknown version.

    We don't know how to parse the version of ND2 that we were given.

    """
    pass

class EmptyFileError(Exception):
    """This .nd2 file seems to be empty.

    Raised if no axes are found in the file.
    """
