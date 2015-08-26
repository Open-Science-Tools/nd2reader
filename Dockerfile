# This is just for functional testing. We install scikit-image just as a convenient way to view images. Many other
# packages could easily accomplish this.

FROM debian:latest
MAINTAINER Jim Rybarski <jim@rybarski.com>

RUN mkdir -p /var/nds2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    liblapack-dev \
    libblas-dev \
    python \
    python3 \
    python-dev \
    python3-dev \
    python-pip \
    python3-pip \
    python-numpy \
    python3-numpy \
    libfreetype6-dev \
    python-numpy \
    python3-numpy \
    python3-matplotlib \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    pkg-config \
    python3-skimage \
    tk \
    tk-dev \
    python3-tk \
 && pip3 install -U cython \
    scikit-image \
 && rm -rf /var/lib/apt/lists/*

COPY . /opt/nd2reader
WORKDIR /opt/nd2reader
RUN python setup.py install
RUN python3 setup.py install
