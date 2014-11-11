from nd2reader import Nd2
from pprint import pprint
import numpy as np
from skimage import io

# n = Nd2("/home/jim/Desktop/nd2hacking/test-141111.nd2")
n = Nd2("/home/jim/Desktop/nd2hacking/YFP-dsRed-GFP-BF.nd2")

# print("Height: ", n.height)
# print("Width: ", n.width)
# for fov in n.fields_of_view:
#     print(fov.number, fov.x, fov.y, fov.z, fov.pfs_offset)
#
for chan in n.channels:
    print(chan.name, chan.camera)
# pprint(len(n.metadata['ImageMetadata']['SLxExperiment']['uLoopPars']['pPeriod']['']))

# res = n.get_image(6)
# print(res[0])
# arr = np.reshape(res[1], (n.height, n.width))
# io.imshow(arr)
# io.show()

# pprint(n.metadata)