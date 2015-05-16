.PHONY: build test shell

build:
	docker build -t jimrybarski/nd2reader .

shell:
	docker run --rm -v ~/Documents/nd2s:/var/nd2s -it jimrybarski/nd2reader
