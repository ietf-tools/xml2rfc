#!/bin/sh

release=$1

tar cvfz ../releases/xml2rfc-$release.tar.gz --transform="s,^\./,xml2rfc-$release/," $(find . -name .svn -prune -o -type f -print)
