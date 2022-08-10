FROM ubuntu:jammy
LABEL maintainer="IETF Tools Team <tools-discuss@ietf.org>"

ENV DEBIAN_FRONTEND noninteractive
WORKDIR /root

# Install dependencies
RUN apt-get update --fix-missing && \
    apt-get install -y --fix-missing \
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
        python3.10 \
        python3.10-dev \
        python3-pip \
        python3.10-distutils && \
    locale-gen en_US.UTF-8

# Install required fonts
RUN mkdir -p ~/.fonts/opentype && \
    wget -q https://noto-website-2.storage.googleapis.com/pkgs/Noto-unhinted.zip && \
    unzip -q Noto-unhinted.zip -d ~/.fonts/opentype/ && \
    rm Noto-unhinted.zip && \
    wget -q https://fonts.google.com/download?family=Roboto%20Mono -O roboto-mono.zip && \
    unzip -q roboto-mono.zip -d ~/.fonts/opentype/ && \
    rm roboto-mono.zip && \
    ln -sf ~/.fonts/opentype/*.[to]tf /usr/share/fonts/truetype/ && \
    fc-cache -f

# Copy everything required to build xml2rfc
COPY requirements.txt setup.py README.md LICENSE Makefile configtest.py .

# Install Python dependencies
RUN pip3 install -r requirements.txt \
    "weasyprint>=53.0" \
    decorator \
    dict2xml \
    "pypdf2>=2.6.0"


COPY xml2rfc ./xml2rfc

# Build xml2rfc & finalize
RUN make install && \
    apt-get remove --purge -y software-properties-common wget unzip && \
    apt-get autoclean && \
    apt-get clean && \
    pip3 uninstall -y decorator dict2xml pypdf2 && \
    rm setup.py Makefile configtest.py requirements.txt && \
    rm -r xml2rfc build dist && \
    echo 'export LANG=en_US.UTF-8' >> ~/.bashrc && \
    echo 'xml2rfc --version' >> ~/.bashrc && \
    echo 'if [ -d ~/xml2rfc ]; then cd ~/xml2rfc; fi' >> ~/.bashrc
