#!/bin/bash
echo "compressing" $1
WAV=$1
FILENAME=$(basename $WAV)
EXTENSIONLESS=${FILENAME%.wav}
M4A=~/render/$EXTENSIONLESS.m4a
echo $M4A
exhale 5 $WAV $M4A
#rm $WAV
echo "done"
