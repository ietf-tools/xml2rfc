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

FROM debian:stretch
LABEL maintainer="Henrik Levkowetz <henrik@levkowetz.com>"

# Default django runserver port
EXPOSE	8000

# Run apt-get noninteractive
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -qy apt-transport-https

# Use backports, updates, and security updates; over https if possible
RUN echo "deb https://deb.debian.org/debian stretch main contrib non-free"  > /etc/apt/sources.list
RUN echo "deb https://deb.debian.org/debian stretch-backports main contrib non-free"  >> /etc/apt/sources.list
RUN echo "deb https://deb.debian.org/debian stretch-updates main contrib non-free" >> /etc/apt/sources.list
RUN echo "deb http://security.debian.org/debian-security stretch/updates main contrib non-free" >> /etc/apt/sources.list

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
	cloc \
	colordiff \
	gcc \
	gnupg2 \
	groff \
	host \
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
	libssl1.0-dev \
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
	python \
	python-dev \
	python-docutils \
	python2.7 \
	python3-cffi \
	python3-dev \
	python3-pip \
	python3-setuptools \
	python3-wheel \
	python3.5 \
	realpath \
	rsync \
	shared-mime-info \
	subversion \
	sudo \
	vim \
        wdiff \
	wget \
	zile \
	zlib1g-dev

# Install SystemV init
RUN apt-get install -qy sysvinit-core \
    && cp /usr/share/sysvinit/inittab /etc/inittab

RUN apt-get install -qy sysvinit-utils

# Get rid of systemd
RUN apt-get remove --yes --purge --auto-remove systemd \
    && echo 'Package: *systemd*\nPin: release *\nPin-Priority: -1\n' > /etc/apt/preferences.d/systemd

# Enable some common locales
RUN sed -i -e 's/^. en_US/en_US/' -e 's/^. en_GB/en_GB/' -e 's/^. en_IE/en_IE/' /etc/locale.gen
RUN locale-gen

# Set up root password
RUN echo "root:root" | chpasswd

# Pip
ENV PYTHONWARNINGS="ignore:a true SSLContext object,ignore:An HTTPS request has been made"
WORKDIR /usr/src
RUN wget -q https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py
RUN pip install certifi
RUN pip install virtualenv
RUN pip install tox
# testing prerequisites
RUN pip install dict2xml pypdf2

# Additional python versions.  Python 3.5 is part of the distribution, 3.4
# and 3.6 not available through apt.

# Python 3.4
WORKDIR /usr/src
RUN wget -q https://www.python.org/ftp/python/3.4.9/Python-3.4.9.tar.xz
RUN tar xJf Python-3.4.9.tar.xz
RUN rm Python-3.4.9.tar.xz
WORKDIR /usr/src/Python-3.4.9/
RUN ./configure
RUN make
RUN make altinstall
WORKDIR /usr/src
RUN rm -rf /usr/src/Python-3.4.9/

# Python 3.6
WORKDIR /usr/src
RUN wget -q https://www.python.org/ftp/python/3.6.8/Python-3.6.8.tar.xz
RUN tar xJf Python-3.6.8.tar.xz
RUN rm Python-3.6.8.tar.xz
WORKDIR /usr/src/Python-3.6.8/
RUN ./configure
RUN make
RUN make altinstall
WORKDIR /usr/src
RUN rm -rf /usr/src/Python-3.6.8/

# Python 3.7
WORKDIR /usr/src
RUN wget -q https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tar.xz
RUN tar xJf Python-3.7.2.tar.xz
RUN rm Python-3.7.2.tar.xz
WORKDIR /usr/src/Python-3.7.2/
RUN ./configure
RUN make
RUN make altinstall
WORKDIR /usr/src/
RUN rm -rf /usr/src/Python-3.7.2/

ENV DDIR="/usr/local/share/xml2rfc"
RUN mkdir -p $DDIR
WORKDIR $DDIR

COPY requirements.txt ./
RUN pip --no-cache-dir install -r requirements.txt

COPY setprompt ./

ENV HOSTNAME=xml2rfc

COPY docker-init.sh /docker-init.sh
RUN chmod +x /docker-init.sh
ENTRYPOINT ["/docker-init.sh"]

CMD	/bin/bash
