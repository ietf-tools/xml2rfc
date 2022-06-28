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
    locales
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

# Update pip
RUN pip install --upgrade pip

# Instal tox
RUN pip3 install tox

WORKDIR /root

# install required fonts
RUN mkdir -p ~/.fonts/opentype
RUN wget -q https://noto-website-2.storage.googleapis.com/pkgs/Noto-unhinted.zip
RUN unzip -q Noto-unhinted.zip -d ~/.fonts/opentype/
RUN wget -q https://fonts.google.com/download?family=Roboto%20Mono -O roboto-mono.zip
RUN unzip -q roboto-mono.zip -d ~/.fonts/opentype/
RUN ln -sf ~/.fonts/opentype/*.[to]tf /usr/share/fonts/truetype/
RUN fc-cache -f

# Copy everything required to build xml2rfc
COPY setup.py .
COPY README.md .
COPY Makefile .
COPY configtest.py .
COPY xml2rfc ./xml2rfc
COPY requirements.txt .

# build xml2rfc
RUN pip3 install -r requirements.txt \
    "weasyprint==55.0" \
    decorator \
    dict2xml \
    typing-extensions \
    pdfplumber
RUN make install

# cleanup
RUN rm Noto-unhinted.zip
RUN rm roboto-mono.zip
RUN apt-get remove --purge -y software-properties-common wget unzip
RUN apt-get autoclean
RUN apt-get clean
RUN pip3 uninstall -y decorator dict2xml typing-extensions pdfplumber
RUN rm setup.py README.md Makefile configtest.py requirements.txt
RUN rm -r xml2rfc build dist

# bash config
RUN echo 'export LANG=en_US.UTF-8' >> ~/.bashrc
RUN echo 'xml2rfc --version' >> ~/.bashrc
RUN echo 'if [ -d ~/xml2rfc ]; then cd ~/xml2rfc; fi' >> ~/.bashrc

ENTRYPOINT bash
