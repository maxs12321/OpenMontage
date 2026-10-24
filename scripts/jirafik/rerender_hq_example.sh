set -e
cd /home/user/OpenMontage/projects/hq
for job in "jirafik-acc6.json:odin-klient" "jirafik-ref5-60.json:ref-vs-partner"; do
  P=${job%%:*}; N=${job##*:}
  echo "[$N] render $(date +%T)"
  (cd /home/user/OpenMontage/remotion-composer && npx remotion render JirafikVlog /home/user/OpenMontage/projects/hq/$N-render.mp4 --props=public/demo-props/$P --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell --image-format=png --crf=12 --concurrency=4 --log=error 2>&1 | grep -vi "webpack\|npm" | tail -3)
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $N-render.mp4); S=$(python3 -c "print($D-0.5)")
  F="fade=t=out:st=$S:d=0.5,format=yuv420p"; A="afade=t=out:st=$S:d=0.5"
  echo "[$N] encode $(date +%T)"
  ffmpeg -loglevel error -y -i $N-render.mp4 -vf "$F" -af "$A" -c:v libx264 -profile:v high -level 4.2 -preset slow -crf 10 -c:a aac -b:a 256k -ar 48000 -movflags +faststart $N-HQ.mp4
  B=$(python3 -c "print(int(28.0*8*1024*1024/$D-192000))")
  ffmpeg -loglevel error -y -i $N-render.mp4 -vf "$F" -af "$A" -c:v libx264 -profile:v high -level 4.2 -preset slow -b:v $B -pass 1 -passlogfile $N -an -f null /dev/null
  ffmpeg -loglevel error -y -i $N-render.mp4 -vf "$F" -af "$A" -c:v libx264 -profile:v high -level 4.2 -preset slow -b:v $B -pass 2 -passlogfile $N -c:a aac -b:a 192k -ar 48000 -movflags +faststart $N-chat.mp4
  ls -la $N-HQ.mp4 $N-chat.mp4
  echo "[$N] READY $(date +%T)"
done
echo ALLDONE
