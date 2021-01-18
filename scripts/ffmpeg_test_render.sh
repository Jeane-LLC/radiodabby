#!/bin/bash

MIDI=$1

echo starting test for $MIDI
ffmpeg -nostdin -re -i $MIDI -c:a libfdk_aac -profile:a aac_he_v2 -ab 48k -content_type 'audio/aac' -vn -f adts icecast://source:ffmpeg@10.17.0.5:8000/test-render

echo done testing $MIDI
