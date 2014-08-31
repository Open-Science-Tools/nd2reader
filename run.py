from nd2reader import Nd2
from pprint import pprint


n = Nd2("/home/jim/code/nd2reader/FYLM-140804-001.nd2")
# print("Height: ", n.height)
# print("Width: ", n.width)
# for fov in n.fields_of_view:
#     print(fov.x, fov.y, fov.z, fov.pfs_offset)
# pprint(n.metadata['ImageMetadataSeq']['SLxPictureMetadata']['sPicturePlanes'])
# for label, channel in n.metadata['ImageMetadataSeq']['SLxPictureMetadata']['sPicturePlanes']['sPlaneNew'].items():
#     print(channel['sDescription'])
#     print(n.metadata['ImageMetadataSeq']['SLxPictureMetadata']['sPicturePlanes']['sSampleSetting'][label]['dExposureTime'])
#     print(n.metadata['ImageMetadataSeq']['SLxPictureMetadata']['sPicturePlanes']['sSampleSetting'][label]['pCameraSetting']['CameraUserName'])

for channel in n.channels:
    print(channel)