cd /home/user/OpenMontage/remotion-composer && npx remotion render JirafikVlog /home/user/OpenMontage/projects/hq/150k-n-render.mp4 --props=public/demo-props/jirafik-150k10n.json --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell --image-format=png --crf=6 --concurrency=4 --log=error 2>&1 | tail -3
cd /home/user/OpenMontage/projects/hq
N=150k-n
ffmpeg -loglevel error -y -i $N-render.mp4 -i ../vid10/b/final_audio_n.wav -map 0:v -map 1:a -c:v copy -c:a pcm_s16le -shortest $N-render2.mov
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $N-render2.mov); S=$(python3 -c "print($D-0.5)")
F="fade=t=out:st=$S:d=0.5,format=yuv420p"; A="afade=t=out:st=$S:d=0.5"
ffmpeg -loglevel error -y -i $N-render2.mov -vf "$F" -af "$A" -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 12 -c:a aac -b:a 256k -ar 48000 -movflags +faststart 150k-3-cheloveka-v2-HQ.mp4
B=$(python3 -c "print(int(28.0*8*1024*1024/$D-192000))")
ffmpeg -loglevel error -y -i $N-render2.mov -vf "$F" -af "$A" -c:v libx264 -profile:v high -level 4.2 -preset slow -b:v $B -pass 1 -passlogfile $N -an -f null /dev/null
ffmpeg -loglevel error -y -i $N-render2.mov -vf "$F" -af "$A" -c:v libx264 -profile:v high -level 4.2 -preset slow -b:v $B -pass 2 -passlogfile $N -c:a aac -b:a 192k -ar 48000 -movflags +faststart 150k-3-cheloveka-v2-chat.mp4
ls -la 150k-3-cheloveka-v2-*.mp4; echo NDONE
