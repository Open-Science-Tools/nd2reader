class InvalidVersionError(Exception):
    """
    We don't know how to parse the version of ND2 that we were given.

    """
    pass


class NoImageError(Exception):
    """
    Some apparent images in ND2s are just completely blank placeholders. These are used when the number of images per
    cycle are unequal (e.g. if you take fluorescent images every 2 minutes, and bright field images every minute).

    """
    pass
