from nd2reader import Nd2
from pprint import pprint
import numpy as np
from skimage import io


n = Nd2("/home/jim/Desktop/nd2hacking/YFP-dsRed-GFP-BF.nd2")
# n = Nd2("/home/jim/Desktop/nd2hacking/test-141111.nd2")
# for chan in n.channels:
#     print(chan.name)
print(n._reader.channel_count)
print(n._z_level_count)
print(n._field_of_view_count)
print(n._timepoint_count)

# z = n._reader.read_coordinates()
# print(z)
# pprint(n._metadata)
image = n._reader.get_raw_image_data(71, 0)
