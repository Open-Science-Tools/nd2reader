FROM ubuntu
MAINTAINER Jim Rybarski <jim@rybarski.com>

RUN apt-get update && apt-get install -y \
  gcc \
  gfortran \
  libblas-dev \
  liblapack-dev \
  libatlas-dev \
  tk \
  tk-dev \
  libpng12-dev \  
  python \
  python-dev \
  python-pip \
  libfreetype6-dev \
  python-skimage
 
RUN pip install numpy
RUN pip install --upgrade scikit-image

COPY . /opt/nd2reader
WORKDIR /opt/nd2reader
RUN python setup.py install
