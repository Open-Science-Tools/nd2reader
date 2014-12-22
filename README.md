nd2reader
=========

## Simple access to hierarchical .nd2 files 

# About

`nd2reader` is a pure-Python package that reads images produced by Nikon microscopes. Though it more or less works, it is currently under development and is not quite ready for use by the general public. Version 1.0 should be released in early 2015.

.nd2 files contain images and metadata, which can be split along multiple dimensions: time, fields of view (xy-axis), focus (z-axis), and filter channel. `nd2reader` allows you to view any subset of images based on any or all of these dimensions.

`nd2reader` holds data in numpy arrays, which makes it trivial to use with the image analysis packages `scikit-image` and `OpenCV`.

# Dependencies

numpy 

# Installation

I'll write this eventually.
