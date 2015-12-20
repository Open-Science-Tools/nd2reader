# This is just for functional testing. We install scikit-image just as a convenient way to view images. Many other
# packages could easily accomplish this.

FROM debian:latest
MAINTAINER Jim Rybarski <jim@rybarski.com>

RUN mkdir -p /var/nds2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    liblapack-dev \
    libblas-dev \
    libatlas3-base \
    python \
    python3 \
    python-dev \
    python3-dev \
    python-pip \
    python3-pip \
    python-numpy \
    python3-numpy \
    libfreetype6-dev \
    python-matplotlib \
    python3-matplotlib \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    pkg-config \
    python-skimage \
    python3-skimage \
    tk \
    tk-dev \
    python-tk \
    python3-tk \
 && pip install -U \
    cython \
    scikit-image \
    xmltodict \
 && pip3 install -U \
    cython \
    scikit-image \
    xmltodict \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/nd2reader
