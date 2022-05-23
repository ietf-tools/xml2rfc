#!/bin/bash

docker --version

echo "Build the image..."
docker build --pull -t xml2rfc .
echo "Starting xml2rfc docker image..."
docker run -it -v ${PWD}:/root/xml2rfc xml2rfc
