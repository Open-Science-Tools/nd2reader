.PHONY: build shell

build:
	docker build -t jimrybarski/nd2reader .

py2shell:
	docker run --rm -v ~/Documents/nd2s:/var/nd2s -it jimrybarski/nd2reader python2.7

py3shell:
	docker run --rm -v ~/Documents/nd2s:/var/nd2s -it jimrybarski/nd2reader python3.4
