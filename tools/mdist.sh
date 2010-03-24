#!/bin/sh

release=$1

files=$(find . -name .svn -prune -o -name tools -prune -o -type f -print)
tar cvfz ../releases/xml2rfc-$release.tar.gz --transform="s,^\./,xml2rfc-$release/," $files

