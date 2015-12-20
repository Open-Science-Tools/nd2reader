## [2.0.0] - 2015-12-20
### ADDED
- `select()` method to rapidly iterate over a subset of images matching certain criteria
- We parse metadata relating to the physical camera used to produce the images
- Raw metadata can be accessed conveniently, to allow contributors to find more interesting things to add
- An XML parsing library was added since the raw metadata contains some XML blocks
- The version number is now available in the nd2reader module
- Created a DOI to allow citation of the code

### REMOVED
- The `ImageGroup` container object
- The `data` attribute on Images. Images now inherit from ndarray, making this redundant
- The `image_sets` iterator

## [1.1.4] - 2015-10-27
### FIXED
- Implemented missing get_image_by_attributes method

## [1.1.3] - 2015-10-16
### FIXED
- ND2s with a single image can now be parsed

## [1.1.2] - 2015-10-09
### ADDED
- `Image` objects now have a `frame_number` attribute.
- `Nd2` can be used as a context manager
- More unit tests and functional tests

### CHANGED
- `Image` objects now directly subclass Numpy arrays
- Refactored code to permit parsing of different versions of ND2s, which will allow us to add support for NIS Elements 3.x.

### DEPRECATED
- The `data` attribute is no longer needed since `Image` is now a Numpy array
- The `image_sets` iterator will be removed in the near future. You should implement this yourself

## [1.1.1] - 2015-09-02
### FIXED
- Images returned by indexing would sometimes be skipped when the file contained multiple channels

### CHANGED
- Dockerfile now installs scikit-image to make visual testing possible

## [1.1.0] - 2015-06-03
### ADDED
- Indexing and slicing of images
- Python 3 support
- Dockerfile support for Python 3.4
- Makefile commands for convenient testing in Docker
- Unit tests

### CHANGED
- Switched to setuptools to automatically install missing dependencies
- Made the interface for most metadata public
- Refactored some poorly-named things

## [1.0.0] - 2015-05-23
### Added
- First stable release!
