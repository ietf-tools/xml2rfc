FROM ubuntu:latest
LABEL maintainer="Kesara Rathnayake <kesara@staff.ietf.org>"

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update --fix-missing
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update --fix-missing

# Install dependencies
RUN apt-get install -y --fix-missing \
    libpango-1.0-0 \
    libssl-dev \
    fontconfig \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    pkg-config \
    libxml2-utils \
    groff \
    wget \
    unzip \
    locales \
    # additional tools
    git \
    vim \
    less

# Set locale
RUN locale-gen en_US.UTF-8

# Install Pythons
# From the OS - Python 3.10
RUN apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    python3.10-distutils

# From deadsnakes
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

# Install required fonts
RUN mkdir -p ~/.fonts/opentype
RUN wget -q https://noto-website-2.storage.googleapis.com/pkgs/Noto-unhinted.zip
RUN unzip -q Noto-unhinted.zip -d ~/.fonts/opentype/
RUN wget -q https://fonts.google.com/download?family=Roboto%20Mono -O roboto-mono.zip
RUN unzip -q roboto-mono.zip -d ~/.fonts/opentype/
RUN ln -sf ~/.fonts/opentype/*.[to]tf /usr/share/fonts/truetype/
RUN fc-cache -f

# Update pip
RUN pip install --upgrade pip

# Install latest packages from PyPI
RUN pip3 install xml2rfc "weasyprint>=53.0" tox

# cleanup
RUN rm Noto-unhinted.zip
RUN rm roboto-mono.zip
RUN apt-get remove --purge -y software-properties-common wget unzip
RUN apt-get autoclean
RUN apt-get clean

# Copy files
COPY README.md .
COPY LICENSE .

# bash config
RUN echo 'export LANG=en_US.UTF-8' >> ~/.bashrc
RUN echo 'xml2rfc --version --verbose' >> ~/.bashrc
RUN echo 'if [ -d ~/xml2rfc ]; then cd ~/xml2rfc; fi' >> ~/.bashrc

ENTRYPOINT bash
