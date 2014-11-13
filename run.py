from nd2reader import Nd2
from pprint import pprint
import numpy as np
from skimage import io


for image_set in Nd2("/home/jim/Desktop/nd2hacking/YFP-dsRed-GFP-BF.nd2").image_sets(0):
    for image in image_set:
        print(image.timestamp, image._channel, image._z_level)
    print("")

# n = Nd2("/home/jim/Desktop/nd2hacking/test-141111.nd2")


