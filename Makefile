.PHONY: build py2shell py3shell test

build:
	docker build -t jimrybarski/nd2reader .

py2:
	docker run --rm -v ~/Documents/nd2s:/var/nd2s -it jimrybarski/nd2reader python2.7

py3:
	docker run --rm -v ~/Documents/nd2s:/var/nd2s -it jimrybarski/nd2reader python3.4

test:	build
	docker run --rm -it jimrybarski/nd2reader python3.4 /opt/nd2reader/tests.py

