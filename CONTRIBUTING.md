# Contributing to nd2reader

We welcome feature proposals and improvements to the library from anyone. If you just have an idea, you can open an [issue](https://github.com/rbnvrw/nd2reader/issues) for
discussion, or get in touch with Ruben Verweij. If you already wrote some code or made changes, simply open a pull
request.

## Running and Writing Tests

Unit tests can be run with the command `python test.py`. The test finder will automatically locate any tests in the `tests` directory. Test classes
must inherit from `unittest.TestCase` and tests will only be run if the function name starts with `test`.

There are also functional tests that work with real ND2s to make sure the code actually works with a wide variety of files. We hope to someday put these into a continuous integration
system so everyone can benefit, but for now, they will just be manually run by the maintainer of this library before merging in any contributions.

## Contributing Your ND2 files

We always appreciate more ND2s, as they help us find corner cases. Please get in touch using any of the means listed at the top of this page if you'd like to send one in.