#!/bin/bash
JCMFILES=./JCS/JCS_audio
for item in $JCMFILES/*.mp3; do ffmpeg -i "$item" -vn -acodec pcm_s16le -ac 1 -ar 44100 -f wav "${item%.*}.wav"; done