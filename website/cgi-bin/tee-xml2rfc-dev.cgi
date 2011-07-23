#!/usr/bin/ksh

d=`date +%Y-%m-%d-%H-%M-%S`
exec 2>/var/tmp/xm.$d.err 
pwd 1>&2

tee /var/tmp/xm.$d.input | ./xml2rfc-dev.cgi | tee /var/tmp/xm.$d.output
