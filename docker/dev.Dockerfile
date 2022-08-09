FROM ghcr.io/ietf-tools/xml2rfc-base:latest
LABEL maintainer="IETF Tools Team <tools-discuss@ietf.org>"

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update --fix-missing
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update --fix-missing

# Install additional tools
RUN apt-get install -y --fix-missing \
    git \
    vim \
    less

# Install Pythons from deadsnakes
# Python 3.10 is already present
RUN apt-get install -y \
    python3.7 \
    python3.7-dev \
    python3.7-distutils \
    python3.8 \
    python3.8-dev \
    python3.8-distutils \
    python3.9 \
    python3.9-dev \
    python3.9-distutils

WORKDIR /root

# Install Python dependencies
RUN pip3 install \
    tox \
    decorator \
    dict2xml \
    "pypdf2>=2.6.0"

# cleanup
RUN apt-get remove --purge -y software-properties-common
RUN apt-get autoclean
RUN apt-get clean

# bash config
RUN echo 'xml2rfc --version --verbose' >> ~/.bashrc

ENTRYPOINT bash
