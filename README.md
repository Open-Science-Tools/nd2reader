# nd2reader

### About

`nd2reader` is a pure-Python package that reads images produced by NIS Elements 4.0+. It has only been definitively tested on NIS Elements 4.30.02 Build 1053. Support for older versions is planned.

.nd2 files contain images and metadata, which can be split along multiple dimensions: time, fields of view (xy-plane), focus (z-plane), and filter channel.

`nd2reader` produces data in numpy arrays, which makes it trivial to use with the image analysis packages such as `scikit-image` and `OpenCV`.

### Installation

Dependencies will automatically be installed if you don't have them. That said, for optimal performance, you should
install the following packages before installing nd2reader:

#### Ubuntu
`apt-get install python-numpy python-six` (Python 2.x)  
`apt-get install python3-numpy python3-six` (Python 3.x)  

#### Other operating systems
These have not been tested yet.

nd2reader is compatible with both Python 2.x and 3.x. I recommend installing using pip:

`pip install nd2reader` (Python 2.x)  
`pip3 install nd2reader` (Python 3.x)

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
Channels: '', 'GFP'
Fields of View: 8
Z-Levels: 3
```

You can also get some metadata about the nd2 programatically:

```python
>>> nd2.height
1280
>>> nd2.width
800
>>> len(nd2)
30528
```

### Images

Every method returns an `Image` object, which contains some metadata about the image as well as the
raw pixel data itself. Images are always a 16-bit grayscale image. The `data` attribute holds the numpy array
with the image data:

```python
>>> image = nd2[20]
>>> print(image.data)
array([[1894, 1949, 1941, ..., 2104, 2135, 2114],
       [1825, 1846, 1848, ..., 1994, 2149, 2064],
       [1909, 1820, 1821, ..., 1995, 1952, 2062],
       ...,
       [3487, 3512, 3594, ..., 3603, 3643, 3492],
       [3642, 3475, 3525, ..., 3712, 3682, 3609],
       [3687, 3777, 3738, ..., 3784, 3870, 4008]], dtype=uint16)
```

You can get a quick summary of image data by examining the `Image` object:

```python
>>> image
<ND2 Image>
1280x800 (HxW)
Timestamp: 1699.79478134
Field of View: 2
Channel: GFP
Z-Level: 1
```

Or you can access it programmatically:

```python
image = nd2[0]
print(image.timestamp)
print(image.field_of_view)
print(image.channel)
print(image.z_level)
```

Often, you may want to just iterate over each image:

```python
import nd2reader
nd2 = nd2reader.Nd2("/path/to/my_images.nd2")
for image in nd2:
    do_something(image.data)
```

You can also get an image directly by indexing. Here, we look at the 38th image:

```python
>>> nd2[37]
<ND2 Image>
1280x800 (HxW)
Timestamp: 1699.79478134
Field of View: 2
Channel: GFP
Z-Level: 1
```

Slicing is also supported and is extremely memory efficient, as images are only read when directly accessed:

```python
my_subset = nd2[50:433]
for image in my_subset:
    do_something(image.data)
```

Step sizes are also accepted:

```python
for image in nd2[:100:2]:
    # gets every other image in the first 100 images
    do_something(image.data)

for image in nd2[::-1]:
    # iterate backwards over every image, if you're into that kind of thing
    do_something(image.data)
```

### Image Sets

If you have complicated hierarchical data, it may be easier to use image sets, which groups images together if they
share the same time index (not timestamp!) and field of view:

```python
import nd2reader
nd2 = nd2reader.Nd2("/path/to/my_complicated_images.nd2")
for image_set in nd2.image_sets:
    # you can select images by channel
    gfp_image = image_set.get("GFP")
    do_something_gfp_related(gfp_image.data)

    # you can also specify the z-level. this defaults to 0 if not given
    out_of_focus_image = image_set.get("Bright Field", z_level=1)
    do_something_out_of_focus_related(out_of_focus_image.data)
```

To get an image from an image set, you must specify a channel. It defaults to the 0th z-level, so if you have
more than one z-level you will need to specify it when using `get`:

```python
image = image_set.get("YFP")
image = image_set.get("YFP", z_level=2)
```

You can also see how many images are in your image set:

```python
>>> len(image_set)
7
```

### Protips

nd2reader is about 14 times faster under Python 3.4 compared to Python 2.7. If you know why, please get in touch!

### Bug Reports and Features

If this fails to work exactly as expected, please open a Github issue. If you get an unhandled exception, please
paste the entire stack trace into the issue as well.

### Contributing

Please feel free to submit a pull request with any new features you think would be useful. You can also create an
issue if you'd just like to propose or discuss a potential idea.

### Acknowledgments

Support for the development of this package was provided by the [Finkelstein Laboratory](http://finkelsteinlab.org/).
