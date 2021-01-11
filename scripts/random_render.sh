#!/bin/bash

TOTAL=$1
PLAYLIST=~/playlists/random-$(uuidgen).m3u

find ~/kunstderfuge | sort -R | tail -$TOTAL | while read FILENAME; do
    echo $FILENAME
    ~/scripts/render.sh $FILENAME $PLAYLIST
done
