# Contributing to nd2reader

We welcome feature proposals and improvements to the library from anyone. If you just have an idea, you can open an [issue](https://github.com/jimrybarski/nd2reader/issues) for
discussion, or get in touch with Jim Rybarski via email at jim@rybarski.com, or on Twitter at @jimrybarski. If you already wrote some code or made changes, simply open a pull
request.

# Easy Tasks for Beginners

There are issues labeled `easy` which are small but useful tasks that are designed for people who are new to open source projects. If you'd like to work on one, feel free to just
take one on, or get in touch if you need help.

# Running and Writing Tests

Unit tests can be run with the commands `python3.4 test.py` and `python2.7 test.py`. The test finder will automatically locate any tests in the `tests` directory. Test classes
must inherit from `unittest.TestCase` and tests will only be run if the function name starts with `test`. If you've built the Docker image, you can also run unit tests with
`make test` - this will conveniently run tests for all supported versions of Python.

There are also functional tests that work with real ND2s to make sure the code actually works with a wide variety of files. We hope to someday put these into a continuous integration
system so everyone can benefit, but for now, they will just be manually run by the maintainer of this library before merging in any contributions.

# Contributing Your ND2 files

We always appreciate more ND2s, as they help us find corner cases. Please get in touch using any of the means listed at the top of this page if you'd like to send one in.

# Docker and Makefile Commands

A Dockerfile is included to allow testing in a consistent environment. `make build` will build the image for you. Due to the large number of packages that it installs, it often
fails due to a problem with the Debian servers - just try again if this happens. Once that's complete, you can run `make py2` or `make py3` to enter into a Python interpreter in
the container to test things out manually. This assumes you have the directory `~/nd2s` - any ND2 files placed there will be available in the container at `/var/nds2`. You can
view images with scikit-image with something like the code below:

```
from nd2reader import Nd2
from skimage import io

n = Nd2("/var/nd2s/my.nd2")
io.imshow(n[37])
io.show()
```
