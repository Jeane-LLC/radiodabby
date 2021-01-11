#!/bin/bash

TOTAL=$1
SOURCEDIR=$2
PLAYLIST=~/playlists/random-$(uuidgen).m3u

find $SOURCEDIR | sort -R | tail -$TOTAL | while read FILENAME; do
    echo $FILENAME
    ~/scripts/render.sh $FILENAME $PLAYLIST
done
