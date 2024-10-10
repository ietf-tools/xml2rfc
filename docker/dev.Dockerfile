FROM ghcr.io/ietf-tools/xml2rfc-base:latest
LABEL maintainer="IETF Tools Team <tools-discuss@ietf.org>"

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /root

# Install dependencies
# libxml2-dev and libxslt-dev are requirements for lxml under Python 3.11
RUN apt-get update --fix-missing && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get install -y --fix-missing \
        git \
        vim \
        less \
        python3.8 \
        python3.8-dev \
        python3.8-distutils \
        python3.9 \
        python3.9-dev \
        python3.9-distutils \
        libxml2-dev \
        libxslt-dev \
        python3.11 \
        python3.11-dev \
        python3.11-distutils \
        python3.12 \
        python3.12-dev \
        python3.12-distutils \
        python3.13 \
        python3.13-dev && \
    rm -rf /var/lib/apt/lists/* /var/log/dpkg.log && \
    apt-get autoremove -y && \
    apt-get clean -y

# Install Python dependencies & finalize
RUN pip3 install \
    tox \
    decorator \
    dict2xml \
    "pypdf>=3.2.1" && \
    git config --global --add safe.directory /root/xml2rfc

ENTRYPOINT bash
