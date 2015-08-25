.PHONY: info build shell py2 py3 test

info:
	@echo ""
	@echo "Available Make Commands"
	@echo ""
	@echo "build:	builds the image"
	@echo "py2:	mounts ~/Documents/nd2s to /var/nd2s and runs a Python 2.7 interpreter"
	@echo "py3:	mounts ~/Documents/nd2s to /var/nd2s and runs a Python 3.4 interpreter"
	@echo "test:	runs all unit tests (in Python 3.4)"
	@echo ""

build:
	docker build -t jimrybarski/nd2reader .

shell:
	docker run --rm -v ~/Documents/nd2s:/var/nd2s -it jimrybarski/nd2reader bash

py2:
	docker run --rm -v ~/Documents/nd2s:/var/nd2s -it jimrybarski/nd2reader python2.7

py3:
	docker run --rm -v ~/Documents/nd2s:/var/nd2s -it jimrybarski/nd2reader python3.4

test:	build
	docker run --rm -it jimrybarski/nd2reader python3.4 /opt/nd2reader/tests.py

