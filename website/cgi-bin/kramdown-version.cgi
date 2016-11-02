#!/bin/bash

echo "Content-Type: text/plain"
echo

basename $(kramdown-rfc2629 --version 2>&1 | sed -e 's/:.*//' -e 's!/bin/.*!!' -e 1q)
ruby --version
