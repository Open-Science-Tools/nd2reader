from nd2reader import Nd2
from pprint import pprint
import six

n = Nd2("/home/jim/nd2s/FYLM-141111-001.nd2")

# for k, v in n._parser.raw_metadata.image_metadata_sequence[b'SLxPictureMetadata'][b'sPicturePlanes'][b'sSampleSetting'][b'a1'].items():
for camera in n._parser._raw_metadata.image_metadata_sequence[b'SLxPictureMetadata'][b'sPicturePlanes'][b'sSampleSetting'].values():
    name = camera[six.b('pCameraSetting')][six.b('CameraUserName')]
    id = camera[six.b('pCameraSetting')][six.b('CameraUniqueName')]
    channel_name = camera[six.b('sOpticalConfigs')][six.b('')][six.b('sOpticalConfigName')]
    x_binning = camera[six.b('pCameraSetting')][six.b('FormatFast')][six.b('fmtDesc')][six.b('dBinningX')]
    y_binning = camera[six.b('pCameraSetting')][six.b('FormatFast')][six.b('fmtDesc')][six.b('dBinningY')]
    exposure = camera[six.b('dExposureTime')]
