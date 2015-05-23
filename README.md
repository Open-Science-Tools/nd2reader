# nd2reader

### About

`nd2reader` is a pure-Python package that reads images produced by NIS Elements.

.nd2 files contain images and metadata, which can be split along multiple dimensions: time, fields of view (xy-plane), focus (z-plane), and filter channel.

`nd2reader` produces data in numpy arrays, which makes it trivial to use with the image analysis packages such as `scikit-image` and `OpenCV`.

### Installation

Just use pip:

`pip install nd2reader`

If you want to install via git, clone the repo and run:

`python setup.py install`

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

### Simple Iteration

For most cases, you'll just want to iterate over each image:

```python
import nd2reader
nd2 = nd2reader.Nd2("/path/to/my_images.nd2")
for image in nd2:
    do_something(image.data)
```

### Image Sets

If you have complicated hierarchical data, it may be easier to use image sets, which groups images together if they
share the same time index and field of view:

```python
import nd2reader
nd2 = nd2reader.Nd2("/path/to/my_complicated_images.nd2")
for image_set in nd2.image_sets:
    # you can select images by channel
    gfp_image = image_set.get("GFP")
    do_something_gfp_related(gfp_image)

    # you can also specify the z-level. this defaults to 0 if not given
    out_of_focus_image = image_set.get("Bright Field", z_level=1)
    do_something_out_of_focus_related(out_of_focus_image)
```

### Direct Image Access

There is a method, `get_image`, which allows random access to images. This might not always return an image, however,
if you acquired different numbers of images in each cycle of a program. For example, if you acquire GFP images every
other minute, but acquire bright field images every minute, `get_image` will return `None` at certain time indexes.

### Images

`Image` objects provide several pieces of useful data.

```python
>>> import nd2reader
>>> nd2 = nd2reader.Nd2("/path/to/my_images.nd2")
>>> image = nd2.get_image(14, 2, "GFP", 1)
>>> image.data
array([[1809, 1783, 1830, ..., 1923, 1920, 1914],
       [1687, 1855, 1792, ..., 1986, 1903, 1889],
       [1758, 1901, 1849, ..., 1911, 2010, 1954],
       ...,
       [3363, 3370, 3570, ..., 3565, 3601, 3459],
       [3480, 3428, 3328, ..., 3542, 3461, 3575],
       [3497, 3666, 3635, ..., 3817, 3867, 3779]])
>>> image.channel
'GFP'
>>> image.timestamp
1699.7947813408175
>>> image.field_of_view
2
>>> image.z_level
1

# You can also get a quick summary of image data:

>>> image
<ND2 Image>
1280x800 (HxW)
Timestamp: 1699.79478134
Field of View: 2
Channel: GFP
Z-Level: 1
```

### Bug Reports and Features

If this fails to work exactly as expected, please open a Github issue. If you get an unhandled exception, please
paste the entire stack trace into the issue as well.

### Contributing

Please feel free to submit a pull request with any new features you think would be useful. You can also create an
issue if you'd just like to propose or discuss a potential idea.