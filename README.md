# nd2reader

### About

`nd2reader` is a pure-Python package that reads images produced by NIS Elements 4.0+. It has only been definitively tested on NIS Elements 4.30.02 Build 1053. Support for older versions is being actively worked on.

.nd2 files contain images and metadata, which can be split along multiple dimensions: time, fields of view (xy-plane), focus (z-plane), and filter channel.

`nd2reader` loads images as Numpy arrays, which makes it trivial to use with the image analysis packages such as `scikit-image` and `OpenCV`.

### Installation

If you don't already have the packages `numpy`, `six` and `xmltodict`, they will be installed automatically:

`pip3 install nd2reader` for Python 3.x

`pip install nd2reader` for Python 2.x

`nd2reader` is an order of magnitude faster in Python 3. I recommend using it unless you have no other choice.

### ND2s

A quick summary of ND2 metadata can be obtained as shown below.
```python
>>> import nd2reader
>>> nd2 = nd2reader.Nd2("/path/to/my_images.nd2")
>>> nd2
<ND2 /path/to/my_images.nd2>
Created: 2014-11-11 15:59:19
Image size: 1280x800 (HxW)
Image cycles: 636
Channels: 'brightfield', 'GFP'
Fields of View: 8
Z-Levels: 3
```

You can iterate over each image in the order they were acquired:

```python
import nd2reader
nd2 = nd2reader.Nd2("/path/to/my_images.nd2")
for image in nd2:
    do_something(image)
```

`Image` objects are just Numpy arrays with some extra metadata bolted on:

```python
>>> image = nd2[20]
>>> image
array([[1894, 1949, 1941, ..., 2104, 2135, 2114],
       [1825, 1846, 1848, ..., 1994, 2149, 2064],
       [1909, 1820, 1821, ..., 1995, 1952, 2062],
       ...,
       [3487, 3512, 3594, ..., 3603, 3643, 3492],
       [3642, 3475, 3525, ..., 3712, 3682, 3609],
       [3687, 3777, 3738, ..., 3784, 3870, 4008]], dtype=uint16)

>>> image.timestamp
10.1241241248
>>> image.frame_number
11
>>> image.field_of_view
6
>>> image.channel
'GFP'
>>> image.z_level
0
```

If you only want to view images that meet certain criteria, you can use `select()`. It's much faster than iterating
and checking attributes of images manually. You can specify scalars or lists of values. Criteria that aren't specified
default to every possible value. Currently, slicing and selecting can't be done at the same time:

```python
for image in nd2.select(channels="GFP", fields_of_view=(1, 2, 7)):
    do_something(image)
```

Slicing is also supported and is extremely memory efficient, as images are only read when directly accessed:

```python
for image in nd2[50:433]:
    do_something(image)

# get every other image in the first 100 images
for image in nd2[:100:2]:
    do_something(image)

# iterate backwards over every image
for image in nd2[::-1]:
    do_something(image)
```

You can also just index a single image:

```python
# gets the 18th image
my_important_image = nd2[17] 
```

The `Nd2` object has some programmatically-accessible metadata: 

```python
>>> nd2.height
1280
>>> nd2.width
800
>>> len(nd2)
30528
```

Each camera has its own settings. If you image multiple wavelengths with one camera, each channel will appear as its
own camera:

```python
>>> nd2.camera_settings
{'GFP': <Camera Settings: GFP>
Camera: Andor Zyla VSC-00461
Camera ID: VSC-00461
Exposure Time (ms): 100.0
Binning: 2x2, 'BF': <Camera Settings: BF>
Camera: Andor Zyla VSC-00461
Camera ID: VSC-00461
Exposure Time (ms): 100.0
Binning: 2x2}
```

Camera information can be accessed programmatically:

```python
>>> nd2.camera_settings['GFP'].id
'VSC-00461'
>>> nd2.camera_settings['GFP'].name
'Andor Zyla VSC-00461'
>>> nd2.camera_settings['GFP'].exposure
100.0
>>> nd2.camera_settings['GFP'].x_binning
2
>>> nd2.camera_settings['GFP'].y_binning
2
```

### How to Cite nd2reader

You can cite nd2reader in your research if you want:

```
Rybarski, Jim (2015): nd2reader. figshare.
http://dx.doi.org/10.6084/m9.figshare.1619960
```

### Bug Reports and Features

If this fails to work exactly as expected, please open a Github issue. If you get an unhandled exception, please
paste the entire stack trace into the issue as well.

### Contributing

Please feel free to submit a pull request with any new features you think would be useful. You can also create an
issue if you'd just like to propose or discuss a potential idea.

### Acknowledgments

Support for the development of this package was provided by the [Finkelstein Laboratory](http://finkelsteinlab.org/).
