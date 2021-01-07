#!/bin/bash
while :
      do
	  for i in $(find /home/arjun/wav/*.wav | sort -R); do
	      ffmpeg -nostdin -re -i $i -c:a libfdk_aac -profile:a aac_he_v2 -ab 48k -content_type 'audio/aac' -vn -f adts icecast://source:ffmpeg@10.17.0.5:8000/radiodabby
	      echo $i
	  done
done
