def get_driver(filename, version):
    """
    Instantiates the correct driver for the ND2, which allows us to parse metadata and access images.

    :param filename:    the path to the ND2
    :type filename:     str
    :param version:     the version of the ND2. Note that this is different than the version of NIS Elements used to create the ND2.
    :type version:      tuple

    """
    return 1
