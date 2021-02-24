#!/bin/bash

MIDI=$1
FILENAME=$(basename $MIDI)
EXTENSIONLESS=${FILENAME%.mid}
WAV=~/wav/$EXTENSIONLESS.wav
pianoteq --preset "Bluethner Model One" --midi $MIDI --wav $WAV
echo "wrote" $WAV
