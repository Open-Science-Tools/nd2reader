# nd2reader

[![Build Status](https://travis-ci.org/rbnvrw/nd2reader.svg?branch=master)](https://travis-ci.org/rbnvrw/nd2reader)
[![Test Coverage](https://codeclimate.com/github/rbnvrw/nd2reader/badges/coverage.svg)](https://codeclimate.com/github/rbnvrw/nd2reader/coverage)
[![Code Climate](https://codeclimate.com/github/rbnvrw/nd2reader/badges/gpa.svg)](https://codeclimate.com/github/rbnvrw/nd2reader)

### About

`nd2reader` is a pure-Python package that reads images produced by NIS Elements 4.0+. It has only been definitively tested on NIS Elements 4.30.02 Build 1053. Support for older versions is being actively worked on.
The reader is written in the [pims](https://github.com/soft-matter/pims) framework, enabling easy access to multidimensional files, lazy slicing, and nice display in IPython.

### Installation

If you don't already have the packages `numpy`, `pims`, `six` and `xmltodict`, they will be installed automatically if you use the `setup.py` script.
`nd2reader` is an order of magnitude faster in Python 3. I recommend using it unless you have no other choice. Python 2.7 and Python >= 3.4 are supported.

### ND2s

`nd2reader` follows the [pims](https://github.com/soft-matter/pims) framework. To open a file:

```python
from nd2reader import ND2Reader
images = ND2Reader('my_directory/example.nd2')
```

After opening the file, all `pims` features are supported. Please refer to the [documentation](http://soft-matter.github.io/pims/).

### Contributing

If you'd like to help with the development of nd2reader or just have an idea for improvement, please see the [contributing](https://github.com/rbnvrw/nd2reader/blob/master/CONTRIBUTING.md) page
for more information.

### Bug Reports and Features

If this fails to work exactly as expected, please open an [issue](https://github.com/rbnvrw/nd2reader/issues).
If you get an unhandled exception, please paste the entire stack trace into the issue as well.

### Acknowledgments

PIMS modified version by Ruben Verweij.

Original version by Jim Rybarski. Support for the development of this package was partially provided by the [Finkelstein Laboratory](http://finkelsteinlab.org/).
