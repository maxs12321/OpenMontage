#!/bin/sh
# iPhone slow-mo section (126.8-2480.1 s) back to real time: video 4x faster (120 fps capture -> 60 fps), audio resampled 4x
set -e
A=126.8; B=2480.1
E="-c:v libx264 -preset veryfast -crf 10 -pix_fmt yuv420p -c:a pcm_s16le -ar 44100"
ffmpeg -loglevel error -y -i raw/src.mov -t $A -vf "fps=60" -af "aresample=44100" $E b/n1.mov
ffmpeg -loglevel error -y -ss $A -to $B -i raw/src.mov -vf "setpts=PTS/4,fps=60" -af "asetrate=176400,aresample=44100" $E b/n2.mov
ffmpeg -loglevel error -y -ss $B -i raw/src.mov -vf "fps=60" -af "aresample=44100" $E b/n3.mov
printf "file 'n1.mov'\nfile 'n2.mov'\nfile 'n3.mov'\n" > b/nlist.txt
ffmpeg -loglevel error -y -f concat -safe 0 -i b/nlist.txt -c copy b/norm.mov
rm b/n1.mov b/n2.mov b/n3.mov
ffprobe -v error -show_entries format=duration,size -of compact b/norm.mov
