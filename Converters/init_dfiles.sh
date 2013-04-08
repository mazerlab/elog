#!/bin/sh

find /auto/data/critters/picard/20?? \
	\( -name 'pic????.*.[0-9][0-9][0-9]' -o \
	   -name 'pic????.*.[0-9][0-9][0-9]'.gz \) |\
  grep -v '0000\.' | grep -v p2m | grep -v .bak | xargs pypenv fill_dfile.py
