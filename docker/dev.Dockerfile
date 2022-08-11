FROM ghcr.io/ietf-tools/xml2rfc-base:latest
LABEL maintainer="IETF Tools Team <tools-discuss@ietf.org>"

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /root

# Install dependencies
RUN apt-get update --fix-missing && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get install -y --fix-missing \
        git \
        vim \
        less \
        python3.7 \
        python3.7-dev \
        python3.7-distutils \
        python3.8 \
        python3.8-dev \
        python3.8-distutils \
        python3.9 \
        python3.9-dev \
        python3.9-distutils

# Install Python dependencies & finalize
RUN pip3 install \
    tox \
    decorator \
    dict2xml \
    "pypdf2>=2.6.0"

ENTRYPOINT bash
