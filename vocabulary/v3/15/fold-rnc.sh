#!/bin/sh
fold -w69 -s < $1 | \
sed 's|^\([-a-zA-Z0-9\]*\)* =|\
<b anchor="grammar.\1">\1</b><iref item="\1 element"/> =|' | \
sed 's|anchor="grammar\.\\|anchor="grammar\.|' | \
sed 's|item="\\|item="|' | \
sed 's|<b anchor="grammar.start">start</b><iref item="start element"/>|start|'
