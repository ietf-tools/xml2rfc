#!/bin/bash

echo Content-Type: text/plain
echo
find /var/tmp/CGI* -mtime +1 -exec rm -rf {} +
