FROM ubuntu:15.04
MAINTAINER Jim Rybarski <jim@rybarski.com>

RUN mkdir -p /var/nds2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libatlas3-base \
    liblapack-dev \
    libblas-dev \
    python \
    python3 \
    python-dev \
    python3-dev \
    python-pip \
    python3-pip

COPY . /opt/nd2reader
WORKDIR /opt/nd2reader
RUN python setup.py install
RUN python3 setup.py install
