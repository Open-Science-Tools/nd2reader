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
