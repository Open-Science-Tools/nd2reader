import collections


class ImageGroup(object):
    """
    A group of images that were taken at roughly the same time and in the same field of view.

    """
    def __init__(self):
        self._images = collections.defaultdict(dict)

    def __len__(self):
        """ The number of images in the image set. """
        return sum([len(channel) for channel in self._images.values()])

    def __repr__(self):
        return "\n".join(["<ND2 Image Group>",
                          "Image count: %s" % len(self)])

    def get(self, channel, z_level=0):
        """
        Retrieve an image with a given channel and z-level. For most users, z_level will always be 0.

        :type channel:  str
        :type z_level:  int

        """
        return self._images.get(channel).get(z_level)

    def add(self, image):
        """
        Stores an image.

        :type image:    nd2reader.model.Image()

        """
        self._images[image.channel][image.z_level] = image
