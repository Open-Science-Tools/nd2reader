import six
import numpy as np


class Roi(object):
    """
    A ND2 ROI representation.
    Coordinates are the center coordinates of the ROI in (x, y, z) order in micron.
    Sizes are the sizes of the ROI in (x, y, z) order in micron.
    Shapes are represented by numbers, defined by constants in this class.
    All these properties can be set for multiple time points (in ms).
    """
    SHAPE_RECTANGLE = 3
    SHAPE_CIRCLE = 9

    TYPE_BACKGROUND = 2

    def __init__(self, raw_roi_dict, metadata):
        """

        :param raw_roi_dict:
        :param metadata
        """
        self.timepoints = []
        self.positions = []
        self.sizes = []
        self.shape = self.SHAPE_CIRCLE
        self.type = self.TYPE_BACKGROUND

        self._width_micron = metadata.width * metadata.pixel_microns
        self._height_micron = metadata.height * metadata.pixel_microns
        self._pixel_microns = metadata.pixel_microns

        self._extract_vect_anims(raw_roi_dict)

    def _extract_vect_anims(self, raw_roi_dict):
        """
        Extract the vector animation parameters from the ROI.
        This includes the position and size at the given timepoints.
        :param raw_roi_dict:
        :return:
        """
        number_of_timepoints = raw_roi_dict[six.b('m_vectAnimParams_Size')]

        for i in range(number_of_timepoints):
            self._parse_vect_anim(raw_roi_dict[six.b('m_vectAnimParams_%d') % i])

        self.shape = raw_roi_dict[six.b('m_sInfo')][six.b('m_uiShapeType')]
        self.type = raw_roi_dict[six.b('m_sInfo')][six.b('m_uiInterpType')]

        # convert to NumPy arrays
        self.timepoints = np.array(self.timepoints, dtype=np.float)
        self.positions = np.array(self.positions, dtype=np.float)
        self.sizes = np.array(self.sizes, dtype=np.float)

    def _parse_vect_anim(self, animation_dict):
        """
        Parses a ROI vector animation object and adds it to the global list of timepoints and positions.
        :param animation_dict:
        :return:
        """
        self.timepoints.append(animation_dict[six.b('m_dTimeMs')])

        position = np.array((self._width_micron / 2.0 + animation_dict[six.b('m_dCenterX')],
                             self._height_micron / 2.0 + animation_dict[six.b('m_dCenterY')],
                             animation_dict[six.b('m_dCenterZ')]))
        self.positions.append(position)

        size_dict = animation_dict[six.b('m_sBoxShape')]

        self.sizes.append((size_dict[six.b('m_dSizeX')],
                           size_dict[six.b('m_dSizeY')],
                           size_dict[six.b('m_dSizeZ')]))

    def is_circle(self):
        return self.shape == self.SHAPE_CIRCLE

    def is_rectangle(self):
        return self.shape == self.SHAPE_RECTANGLE
