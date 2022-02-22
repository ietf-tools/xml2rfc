# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.217.4/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.10-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends groff html2text python3-cffi python3-brotli libpango-1.0-0 libcairo2-dev libjpeg-dev libgif-dev librsvg2-dev libharfbuzz0b libpangoft2-1.0-0 libxml2-dev libxml2-utils

# [Optional] Uncomment this line to install global node packages.
# RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g <your-package-here>" 2>&1

RUN echo "Downloading Noto Font..." \
    && mkdir -p ~/.fonts/opentype/noto \
    && wget -q https://noto-website-2.storage.googleapis.com/pkgs/Noto-unhinted.zip \
    && unzip -q Noto-unhinted.zip -d ~/.fonts/opentype/noto/ \
    && mkdir -p /usr/share/fonts/truetype/noto/ \
    && ln -sf ~/.fonts/opentype/noto/*.[to]tf /usr/share/fonts/truetype/noto/ \
    && echo "Downloading Roboto Mono Font..." \
    && mkdir -p ~/.fonts/opentype/roboto \
    && wget -q https://fonts.google.com/download?family=Roboto%20Mono -O roboto-mono.zip \
    && unzip -q roboto-mono.zip -d ~/.fonts/opentype/roboto/ \
    && mkdir -p /usr/share/fonts/truetype/roboto/ \
    && ln -sf ~/.fonts/opentype/roboto/*.[to]tf /usr/share/fonts/truetype/roboto/ \
    && echo "Reloading Font Cache..." \
    && fc-cache -f -v

RUN pip3 --disable-pip-version-check --no-cache-dir install --upgrade pip wheel
RUN pip3 --disable-pip-version-check --no-cache-dir install tox certifi decorator dict2xml==1.7 "pycairo<1.20" PyPDF2 "weasyprint<53"