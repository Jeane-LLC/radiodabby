#!/bin/bash

MIDI=$1
IC1=$2
IC2=$3

$SIGMA = 10.0
$RHO = 28.0
$BETA = 8.0/3.0

python3 ~/scripts/chaotic_mapping.py --filename $MIDI --mapping dabby --lorenz0 100 10000 1.0 1.0 1.0 $RHO $SIGMA $BETA --lorenz1 100 10000 0.999 1.0 1.0 $RHO $SIGMA $BETA
