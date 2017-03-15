"""
Functions to create artificial nd2 data for testing purposes
"""
import six


class ArtificialND2(object):
    """
    Artificial ND2 class (for testing purposes)
    """

    def __init__(self, file):
        self._fh = open(file, 'wb')
        self.write_version()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @property
    def file_handle(self):
        """
        The file handle to the binary file
        Returns:
            file: the file handle
        """
        return self._fh

    def close(self):
        """
        Correctly close the file handle
        """
        if self._fh is not None:
            self._fh.close()

    def write_version(self):
        """
        Write file header
        """
        # write 16 empty bytes
        self._fh.write(bytearray(16))

        # write version info
        version_info = six.b('ND2 FILE SIGNATURE CHUNK NAME01!Ver3.0')
        self._fh.write(version_info)
