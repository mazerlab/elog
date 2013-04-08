#!/bin/sh

#pypenv ./newdb.py
pypenv ./fill_notes.py picard </auto/data/critters/picard/picard_2004.log
pypenv ./fill_notes.py picard </auto/data/critters/picard/picard_2005.log
pypenv ./fill_notes.py picard </auto/data/critters/picard/picard.log
pypenv ./fill_notes.py flea </auto/data/critters/flea/flea.log
pypenv ./fill_notes.py mercutio </auto/data/critters/mercutio/mercutio.log


