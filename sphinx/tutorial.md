# Tutorial

### Installation

For now, the package is only available via GitHub. Install it using:

```
pip install --upgrade https://github.com/rbnvrw/nd2reader/tarball/master
```

If you don't already have the packages `numpy`, `pims`, `six` and `xmltodict`, they will be installed automatically if you use the `setup.py` script.
`nd2reader` is an order of magnitude faster in Python 3. I recommend using it unless you have no other choice. Python 2.7 and Python >= 3.4 are supported.

### Opening ND2s

`nd2reader` follows the [pims](https://github.com/soft-matter/pims) framework. To open a file and show the first frame:

```python
from nd2reader import ND2Reader
import matplotlib.pyplot as plt

with ND2Reader('my_directory/example.nd2') as images:
  plt.imshow(images[0])
```

After opening the file, all `pims` features are supported. Please refer to the [pims documentation](http://soft-matter.github.io/pims/).