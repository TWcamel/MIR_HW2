#!/bin/bash
# ffmpeg -i *.mp3 -vn -acodec pcm_s16le -ac 1 -ar 44100 -f wav *.wav -y
for item in ./JCS/JCS_audio/*.mp3; do ffmpeg -i "$item" -vn -acodec pcm_s16le -ac 1 -ar 44100 -f wav "${item%.*}.wav"; done