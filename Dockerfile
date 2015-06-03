FROM ubuntu:15.04
MAINTAINER Jim Rybarski <jim@rybarski.com>

RUN mkdir -p /var/nds2
RUN apt-get update && apt-get install -y --no-install-recommends \
    python-numpy \
    python3-numpy \
    python-pip \
    python3-pip

RUN pip install six
RUN pip3 install six

COPY . /opt/nd2reader
WORKDIR /opt/nd2reader
RUN python setup.py install
RUN python3 setup.py install
