# Tutorial

### Installation

The package is available on PyPi. Install it using:

```
pip install nd2reader
```

If you don't already have the packages `numpy`, `pims`, `six` and `xmltodict`, they will be installed automatically if you use the `setup.py` script.
`nd2reader` is an order of magnitude faster in Python 3. I recommend using it unless you have no other choice. Python 2.7 and Python >= 3.4 are supported.

#### Installation via Conda Forge

Installing `nd2reader` from the `conda-forge` channel can be achieved by adding `conda-forge` to your channels with:

```
conda config --add channels conda-forge
```

Once the `conda-forge` channel has been enabled, `nd2reader` can be installed with:

```
conda install nd2reader
```

It is possible to list all of the versions of `nd2reader` available on your platform with:

```
conda search nd2reader --channel conda-forge
```

### Opening ND2s

`nd2reader` follows the [pims](https://github.com/soft-matter/pims) framework. To open a file and show the first frame:

```python
from nd2reader import ND2Reader
import matplotlib.pyplot as plt

with ND2Reader('my_directory/example.nd2') as images:
  plt.imshow(images[0])
```

After opening the file, all `pims` features are supported. Please refer to the [pims documentation](http://soft-matter.github.io/pims/).

### ND2 metadata

The ND2 file contains various metadata, such as acquisition information,
regions of interest and custom user comments. Most of this metadata is parsed
and available in dictionary form. For example:

```python
from nd2reader import ND2Reader

with ND2Reader('my_directory/example.nd2') as images:
    # width and height of the image
    print('%d x %d px' % (images.metadata['width'], images.metadata['height']))
```

All metadata properties are:

* `width`: the width of the image in pixels
* `height`: the height of the image in pixels
* `date`: the date the image was taken 
* `fields_of_view`: the fields of view in the image
* `frames`: a list of all frame numbers
* `z_levels`: the z levels in the image
* `total_images_per_channel`: the number of images per color channel
* `channels`: the color channels
* `pixel_microns`: the amount of microns per pixel
* `rois`: the regions of interest (ROIs) defined by the user
* `experiment`: information about the nature and timings of the ND experiment

### Iterating over fields of view

Using `NDExperiments` in the Nikon software, it is possible to acquire images on different `(x, y)` positions. 
This is referred to as different fields of view. Using this reader, the fields of view are on the `v` axis. 
For example:
```python
from nd2reader import ND2Reader

with ND2Reader('my_directory/example.nd2') as images:
    # width and height of the image
    print(images.metadata)
```
will output
```python
{'channels': ['BF100xoil-1x-R', 'BF+RITC'],
 'date': datetime.datetime(2017, 10, 30, 14, 35, 18),
 'experiment': {'description': 'ND Acquisition',
  'loops': [{'duration': 0,
    'sampling_interval': 0.0,
    'start': 0,
    'stimulation': False}]},
 'fields_of_view': [0, 1],
 'frames': [0],
 'height': 1895,
 'num_frames': 1,
 'pixel_microns': 0.09214285714285715,
 'total_images_per_channel': 6,
 'width': 2368,
 'z_levels': [0, 1, 2]}
```
for our example file. As you can see from the metadata, it has two fields of view. We can also look at the sizes of the axes:
```python
    print(images.sizes)
```
```python
{'c': 2, 't': 1, 'v': 2, 'x': 2368, 'y': 1895, 'z': 3}
```
As you can see, the fields of view are listed on the `v` axis. It is therefore possible to loop over them like this:
```python
    images.iter_axes = 'v'
    for fov in images:
        print(fov) # Frame containing one field of view
```
For more information on axis bundling and iteration, refer to the [pims documentation](http://soft-matter.github.io/pims/v0.4/multidimensional.html#axes-bundling).
