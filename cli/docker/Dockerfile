# -*- shell-mode -*-
# This file is a docker (https://www.docker.com/what-docker) recipe, which can be used to build
# a docker image which is ready to run a datatracker in development mode.
#
# It is used to build an image (once you've installed docker) using a command like this (assuming
# suitable replacement of $variables:
#
#	$ docker build -t $yourdockerid/datatracker:$version
#
# To use a pre-built image, assuming we're on OS X and have a checked-out datatracker repository
# at /Users/$login/src/6.8.1.dev0, you would start (again assuming you've installed docker)
# a container from an image, as follows:
# 
#	$ docker run -ti --name=$containername -v /Users/$login:/home/$login levkowetz/datatracker:$version /bin/bash
# 
# This maps your home directory to /home/$login in the container, and starts it running /bin/bash.
# 
# In this first version, the docker environment is set up so that tests will run successfully,
# but the database has *not* been loaded with a dump, and supporting files (drafts, charters, etc.)
# have *not* been downloaded.

FROM dyne/devuan:beowulf
LABEL maintainer="Henrik Levkowetz <henrik@levkowetz.com>"

# Run apt-get noninteractive
ENV DEBIAN_FRONTEND=noninteractive
ENV DEVUAN_FRONTEND=noninteractive

RUN apt-get update --allow-releaseinfo-change
RUN apt-get install -qy apt-transport-https

# Use backports, updates, and security updates
RUN echo "deb http://deb.devuan.org/merged beowulf main contrib non-free"  > /etc/apt/sources.list
RUN echo "deb http://deb.devuan.org/merged beowulf-security main contrib non-free" >> /etc/apt/sources.list
RUN echo "deb http://deb.devuan.org/merged beowulf-updates main contrib non-free" >> /etc/apt/sources.list
RUN echo "deb http://deb.devuan.org/merged beowulf-backports main contrib non-free" >> /etc/apt/sources.list

# Remove some excludes for the docker image
RUN sed -i -e '/^path-exclude=.*\/groff/d' \
           -e '/^path-exclude=.*\/locale/d' \
           -e '/^path-exclude=.*\/man/d' /etc/dpkg/dpkg.cfg.d/docker-excludes

# Install needed packages
#
# We're not including graphviz and ghostscript, needed for the 3 document
# dependency graph tests; they would increase the size of the image by about
# 15%, about 100MB.

# Fetch apt package information, and upgrade to latest package versions
RUN apt-get update
RUN apt-get -qy upgrade

# Install the packages we need
RUN apt-get install -qy \
	build-essential \
	bzip2 \
	ca-certificates \
	colordiff \
	gcc \
	gnupg2 \
	groff \
        html2text \
	ipython \
	less \
	libbz2-dev \
	libcairo2 \
	libcairo2-dev \
	libdb5.3-dev \
	libexpat1-dev \
	libffi-dev \
	libfontconfig1 \
	libfontconfig1-dev \
	libfreetype6 \
	libgdbm-dev \
	libgdk-pixbuf2.0-0 \
	liblzma-dev \
	libncurses5-dev \
	libncursesw5-dev \
	libpango-1.0-0 \
	libpango1.0-0 \
	libpangocairo-1.0-0 \
	libreadline-dev \
	libsqlite3-dev \
	libssl-dev \
	libxml2-dev \
	libxml2-utils \
	libxslt-dev \
	libz-dev \
	locales \
	make \
	man \
	openssh-client \
	patch \
	procps \
	python3.5 \
	python3-cffi \
	python3-dev \
	python3-pip \
	python3-setuptools \
	python3-wheel \
	rsync \
	shared-mime-info \
	subversion \
	sudo \
	vim \
        wdiff \
	wget \
	zile \
	zlib1g-dev

# Get rid of installation files we don't need in the image, to reduce size
RUN du -sm /var/lib/apt/lists/
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Enable some common locales
RUN sed -i -e 's/^. en_US/en_US/' -e 's/^. en_GB/en_GB/' -e 's/^. en_IE/en_IE/' /etc/locale.gen
RUN locale-gen

# Set up root password
RUN echo "root:root" | chpasswd

# Additional python versions.

# Python 3.5
WORKDIR /usr/src
RUN wget -q https://www.python.org/ftp/python/3.5.9/Python-3.5.9.tar.xz
RUN tar xJf Python-3.5.9.tar.xz
RUN rm Python-3.5.9.tar.xz
WORKDIR /usr/src/Python-3.5.9/
RUN ./configure
RUN make
RUN make altinstall
WORKDIR /usr/src
RUN rm -rf /usr/src/Python-3.5.9/

# Python 3.6
WORKDIR /usr/src
RUN wget -q https://www.python.org/ftp/python/3.6.10/Python-3.6.10.tar.xz
RUN tar xJf Python-3.6.10.tar.xz
RUN rm Python-3.6.10.tar.xz
WORKDIR /usr/src/Python-3.6.10/
RUN ./configure
RUN make
RUN make altinstall
WORKDIR /usr/src
RUN rm -rf /usr/src/Python-3.6.10/

# Python 3.7
WORKDIR /usr/src
RUN wget -q https://www.python.org/ftp/python/3.7.6/Python-3.7.6.tar.xz
RUN tar xJf Python-3.7.6.tar.xz
RUN rm Python-3.7.6.tar.xz
WORKDIR /usr/src/Python-3.7.6/
RUN ./configure
RUN make
RUN make altinstall
WORKDIR /usr/src/
RUN rm -rf /usr/src/Python-3.7.6/

# Python 3.8
WORKDIR /usr/src
RUN wget -q https://www.python.org/ftp/python/3.8.1/Python-3.8.1.tar.xz
RUN tar xJf Python-3.8.1.tar.xz
RUN rm Python-3.8.1.tar.xz
WORKDIR /usr/src/Python-3.8.1/
RUN ./configure
RUN make
RUN make altinstall
WORKDIR /usr/src/
RUN rm -rf /usr/src/Python-3.8.1/

ENV DDIR="/usr/local/share/xml2rfc"
RUN mkdir -p $DDIR
WORKDIR $DDIR

COPY requirements.txt ./
RUN pip3 --no-cache-dir install -r requirements.txt certifi decorator dict2xml pypdf2 tox weasyprint

COPY setprompt ./

ENV HOSTNAME=xml2rfc

COPY docker-init.sh /docker-init.sh
RUN chmod +x /docker-init.sh
ENTRYPOINT ["/docker-init.sh"]

CMD	/bin/bash
