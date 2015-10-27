# nd2reader

`nd2reader` is a pure-Python package that reads images produced by NIS Elements 4.0+. It has only been definitively tested on NIS Elements 4.30.02 Build 1053. Support for older versions is planned.

.nd2 files contain images and metadata, which can be split along multiple dimensions: time, fields of view (xy-plane), focus (z-plane), and filter channel.

`nd2reader` loads images as Numpy arrays, which makes it trivial to use with the image analysis packages such as `scikit-image` and `OpenCV`.

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

`Nd2` is also a context manager, if you care about that sort of thing:

```
>>> import nd2reader
>>> with nd2reader.Nd2("/path/to/my_images.nd2") as nd2:
...     for image in nd2:
...         do_something(image)
```

### Images

`Image` objects are just Numpy arrays with some extra metadata bolted on:

```python
>>> image = nd2[20]
>>> print(image)
array([[1894, 1949, 1941, ..., 2104, 2135, 2114],
       [1825, 1846, 1848, ..., 1994, 2149, 2064],
       [1909, 1820, 1821, ..., 1995, 1952, 2062],
       ...,
       [3487, 3512, 3594, ..., 3603, 3643, 3492],
       [3642, 3475, 3525, ..., 3712, 3682, 3609],
       [3687, 3777, 3738, ..., 3784, 3870, 4008]], dtype=uint16)

>>> print(image.timestamp)
10.1241241248
>>> print(image.frame_number)
11
>>> print(image.field_of_view)
6
>>> print(image.channel)
'GFP'
>>> print(image.z_level)
0
```

Often, you may want to just iterate over each image in the order they were acquired:

```python
import nd2reader
nd2 = nd2reader.Nd2("/path/to/my_images.nd2")
for image in nd2:
    do_something(image)
```

Slicing is also supported and is extremely memory efficient, as images are only read when directly accessed:

```python
my_subset = nd2[50:433]
for image in my_subset:
    do_something(image)
```

Step sizes are also accepted:

```python
for image in nd2[:100:2]:
    # gets every other image in the first 100 images
    do_something(image)

for image in nd2[::-1]:
    # iterate backwards over every image, if you're into that kind of thing
    do_something(image)
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
