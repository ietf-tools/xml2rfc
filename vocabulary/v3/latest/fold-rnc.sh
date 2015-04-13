#!/bin/sh
fold -w69 -s < $1 | \
sed 's|^\([-a-zA-Z0-9\]*\)* =|\
<strong anchor="grammar.\1">\1</strong><iref item="\1 element"/> =|' | \
sed 's|anchor="grammar\.\\|anchor="grammar\.|' | \
sed 's|item="\\|item="|' | \
sed 's|<strong anchor="grammar.start">start</strong><iref item="start element"/>|start|'
