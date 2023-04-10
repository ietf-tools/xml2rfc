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
RUN mkdir -p ~/.fonts/opentype && \
    wget -q https://noto-website-2.storage.googleapis.com/pkgs/Noto-unhinted.zip && \
    unzip -q Noto-unhinted.zip -d ~/.fonts/opentype/ && \
    rm Noto-unhinted.zip && \
    wget -q https://fonts.google.com/download?family=Roboto%20Mono -O roboto-mono.zip && \
    unzip -q roboto-mono.zip -d ~/.fonts/opentype/ && \
    rm roboto-mono.zip && \
    wget -q https://fonts.google.com/download?family=Noto%20Sans%20Math -O noto-sans-math.zip && \
    unzip -q noto-sans-math.zip -d ~/.fonts/opentype/ && \
    rm noto-sans-math.zip && \
    ln -sf ~/.fonts/opentype/*.[to]tf /usr/share/fonts/truetype/ && \
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
    "weasyprint>=53.0" \
    decorator \
    dict2xml \
    "pypdf>=3.2.1"

COPY xml2rfc ./xml2rfc

# Build xml2rfc & finalize
RUN make install && \
    pip3 uninstall -y decorator dict2xml pypdf && \
    rm setup.py Makefile configtest.py requirements.txt && \
    rm -r xml2rfc build
