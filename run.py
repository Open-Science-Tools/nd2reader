from nd2reader import Nd2
from pprint import pprint


n = Nd2("/home/jim/Desktop/nd2hacking/BFonly.nd2")
print("Height: ", n.height)
print("Width: ", n.width)
for fov in n.fields_of_view:
    print(fov.number, fov.x, fov.y, fov.z, fov.pfs_offset)

for channel in n.channels:
    print(channel.name)
    print(channel.camera)
    print(channel.exposure_time)

print(n.get_image(3))