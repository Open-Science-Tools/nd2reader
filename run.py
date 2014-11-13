from nd2reader import Nd2
from pprint import pprint
import numpy as np
from skimage import io


for image in Nd2("/home/jim/Desktop/nd2hacking/YFP-dsRed-GFP-BF.nd2"):

# n = Nd2("/home/jim/Desktop/nd2hacking/test-141111.nd2")


    image.show()