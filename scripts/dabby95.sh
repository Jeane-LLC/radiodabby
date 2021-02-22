#!/bin/bash

MIDI=$1
TMAX=$2
TSTEP=$3
XI=$4
YI=$5
ZI=$6
XJ=$7
YJ=$8
ZJ=$9
SIGMA=10.0
RHO=28.0
BETA=8.0/3.0

python3 ~/scripts/chaotic_mapping.py --filename $MIDI --mapping dabby --lorenz0 $TMAX $TSTEP $XI $YI $ZI $RHO $SIGMA $BETA --lorenz1 $TMAX $TSTEP $XJ $YJ $ZJ $RHO $SIGMA $BETA
