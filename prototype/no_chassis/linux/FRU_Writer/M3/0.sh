#!/bin/sh

QPN=$(basename $0 .sh)
FPATH=../../../FRU/M3/#Marker
UTIL=../../bmcfwtool

$UTIL fwtool fru bin 255 $FPATH/$QPN.txt $FPATH/FRU.ini $1
