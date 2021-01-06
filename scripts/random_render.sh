#!/bin/bash

TOTAL=$1
PLAYLIST=/home/arjun/playlists/random-$(uuidgen).m3u

find /home/arjun/kunstderfuge | sort -R | tail -$TOTAL | while read FILENAME; do
    echo $FILENAME
    /home/arjun/scripts/render.sh $FILENAME $PLAYLIST
done
