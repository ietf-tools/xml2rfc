FROM ubuntu:jammy
LABEL maintainer="IETF Tools Team <tools-discuss@ietf.org>"

ENV DEBIAN_FRONTEND noninteractive
ENV LANG=en_US.UTF-8

WORKDIR /root

# .bashrc configuration
RUN echo 'xml2rfc --version' >> ~/.bashrc && \
    echo 'if [ -d ~/xml2rfc ]; then cd ~/xml2rfc; fi' >> ~/.bashrc

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
    locale-gen en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/* /var/log/dpkg.log && \
    apt-get autoremove -y && \
    apt-get clean -y

# Install required fonts
RUN mkdir -p ~/.fonts/opentype /tmp/fonts && \
    wget -q -O /tmp/fonts.tar.gz https://github.com/ietf-tools/xml2rfc-fonts/archive/refs/tags/3.21.0.tar.gz && \
    tar zxf /tmp/fonts.tar.gz -C /tmp/fonts && \
    mv /tmp/fonts/*/noto/* ~/.fonts/opentype/ && \
    mv /tmp/fonts/*/roboto_mono/* ~/.fonts/opentype/ && \
    rm -rf /tmp/fonts.tar.gz /tmp/fonts/ && \
    fc-cache -f

# Copy everything required to build xml2rfc
COPY requirements.txt setup.py setup.cfg pyproject.toml README.md LICENSE Makefile configtest.py .


# Install & update build tools
RUN pip3 install --upgrade \
    pip \
    setuptools \
    wheel

# Install Python dependencies
RUN pip3 install -r requirements.txt \
    "weasyprint>=53.0,!=57.0,!=60.0" \
    decorator \
    dict2xml \
    "pypdf>=3.2.1"

COPY xml2rfc ./xml2rfc

# Build xml2rfc & finalize
RUN make install && \
    pip3 uninstall -y decorator dict2xml pypdf && \
    rm setup.py Makefile configtest.py requirements.txt && \
    rm -r xml2rfc build
