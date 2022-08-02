#!/bin/bash

docker --version

if [[ "$(docker images -q xml2rfc-base:latest 2> /dev/null)" == "" ]]; then
    echo "Build the image xml2rfc-base:latest"
    docker build -f docker/base.Dockerfile --pull -t xml2rfc-base:latest .
else
    echo "xml2rfc-base:latest already exists."
    echo "To update xml2rfc-base, run:"
    echo "      docker rmi xml2rfc-base:latest"
    echo "and rerun this script."
fi

echo "Build the image xml2rfc-dev"
docker build -f docker/dev.Dockerfile -t xml2rfc-dev .

echo "Starting xml2rfc docker image..."
docker run -it -v ${PWD}:/root/xml2rfc xml2rfc-dev
