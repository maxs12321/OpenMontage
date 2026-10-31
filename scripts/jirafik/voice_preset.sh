#!/bin/sh
# Funny-video voice (only when Ilya asks for it, NOT the default): -2.25 semitones, strong low end, dark top, silent pauses.
# Usage: voice_preset.sh in.wav out.wav   (apply to the voice before mixing SFX/music)
R=$(python3 -c "print(2**(-2.25/12))")
ffmpeg -loglevel error -y -i "$1" -af "rubberband=pitch=$R:transients=smooth:formant=shifted,highpass=f=60,afftdn=nr=12:nf=-45,lowshelf=f=130:g=8,equalizer=f=900:t=q:w=1.0:g=-4,highshelf=f=2500:g=-9,lowpass=f=9000,acompressor=threshold=-26dB:ratio=5:attack=6:release=100:makeup=5,agate=threshold=0.02:ratio=4:attack=5:release=150,loudnorm=I=-14:TP=-1.5:LRA=6" "$2"
