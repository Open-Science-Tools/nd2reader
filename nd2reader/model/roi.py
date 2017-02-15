import six
import numpy as np


class Roi(object):
    """
    A ND2 ROI representation.
    Coordinates are the center coordinates of the ROI in (x, y, z) order.
    Sizes are the sizes of the ROI in (x, y, z) order.
    Shapes are represented by numbers, defined by constants in this class.
    All these properties can be set for multiple timepoints.
    """
    SHAPE_RECTANGLE = 3
    SHAPE_CIRCLE = 9

    def __init__(self, raw_roi_dict):
        self.timepoints = []
        self.positions = []
        self.sizes = []
        self.shapes = []

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
            shape = raw_roi_dict[six.b('m_sInfo')][six.b('m_uiShapeType')]
            self._parse_vect_anim(raw_roi_dict[six.b('m_vectAnimParams_%d') % i], shape)

        # convert to NumPy arrays
        self.timepoints = np.array(self.timepoints, dtype=np.float)
        self.positions = np.array(self.positions, dtype=np.float)
        self.sizes = np.array(self.sizes, dtype=np.float)
        self.shapes = np.array(self.shapes, dtype=np.uint)

    def _parse_vect_anim(self, animation_dict, shape):
        """
        Parses a ROI vector animation object and adds it to the global list of timepoints and positions.
        :param animation_dict:
        :return:
        """
        self.timepoints.append(animation_dict[six.b('m_dTimeMs')])
        self.positions.append((animation_dict[six.b('m_dCenterX')],
                               animation_dict[six.b('m_dCenterY')],
                               animation_dict[six.b('m_dCenterZ')]))
        size_dict = animation_dict[six.b('m_sBoxShape')]
        self.sizes.append((size_dict[six.b('m_dSizeX')],
                           size_dict[six.b('m_dSizeY')],
                           size_dict[six.b('m_dSizeZ')]))
        self.shapes.append(shape)

    def is_circle(self, timepoint_id=0):
        return self.shapes[timepoint_id] == self.SHAPE_CIRCLE

    def is_rectangle(self, timepoint_id=0):
        return self.shapes[timepoint_id] == self.SHAPE_RECTANGLE
