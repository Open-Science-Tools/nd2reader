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


