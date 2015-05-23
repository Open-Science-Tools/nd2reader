FROM ubuntu
MAINTAINER Jim Rybarski <jim@rybarski.com>

RUN mkdir -p /var/nds2
RUN apt-get update && apt-get install -y \
    python-numpy

COPY . /opt/nd2reader
WORKDIR /opt/nd2reader
RUN python setup.py install
WORKDIR /var/nd2s

CMD /usr/bin/python2.7
