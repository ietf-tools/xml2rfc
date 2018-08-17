#!/usr/bin/ksh

d=`date +%Y-%m-%d-%H-%M-%S`
exec 2>/var/tmp/xm.$d.err 
pwd > /var/tmp/xm.$d.pwd
env > /var/tmp/xm.$d.env

tee /var/tmp/xm.$d.input | ./xml2rfc.cgi | tee /var/tmp/xm.$d.output
