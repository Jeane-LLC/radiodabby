#!/bin/bash

MIDI=$1
M3U=$2
FILENAME=$(basename $MIDI)
EXTENSIONLESS=${FILENAME%.mid}
WAV=/home/arjun/wav/$EXTENSIONLESS.wav
M4A=/home/arjun/render/$EXTENSIONLESS.m4a
echo $MIDI $M3U $WAV $M4A
pianoteq --preset "Bluethner Model One" --midi $MIDI --wav $WAV
#exhale 5 $WAV $M4A
#rm $WAV
#cat $M4A >> $M3U
cat $WAV >> $M3U
echo "done"
