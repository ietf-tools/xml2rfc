#!/bin/bash

docker run -it $@ -v ${PWD}:/root/xml2rfc ghcr.io/ietf-tools/xml2rfc-dev:latest
