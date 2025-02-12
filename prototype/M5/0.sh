#!/bin/sh

UTIL=../fruid-util.py
BIN=${1:-fru.bin}

#Default_Markers

#Stage_Markers

#Modify_Markers

# show the result
python3 $UTIL $BIN

