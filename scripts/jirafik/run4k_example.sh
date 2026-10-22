set -e
cd /home/user/OpenMontage/projects/vid5
PY=/home/user/OpenMontage/.venv/bin/python
echo "[1] prep $(date +%T)"
$PY prep4k.py; $PY prep_pv4k.py
echo "[2] segments $(date +%T)"
ffmpeg -loglevel error -y -i b4k/p_3452_2.mp4 -i b4k/p_3452_base.mp4 -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 14 -preset fast -c:a aac -b:a 256k b4k/A.mp4
ffmpeg -loglevel error -y -i b4k/p_3452_3.mp4 -i b4k/p_3452_4.mp4 -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 14 -preset fast -c:a aac -b:a 256k b4k/D.mp4
ffmpeg -loglevel error -y -i b4k/p_3453_3.mp4 -i b4k/p_3453_4.mp4 -i b4k/p_3453_5.mp4 -i b4k/p_3453_6.mp4 -i b4k/p_3454_4.mp4 -ss 13.0 -t 7.15 -i raw/v2.mov -filter_complex "[0:v][1:v][2:v][3:v][4:v]concat=n=5:v=1:a=0,trim=duration=7.15,setpts=PTS-STARTPTS[v];[5:a]aresample=48000,afade=t=in:d=0.03,afade=t=out:st=7.1:d=0.05[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 14 -preset fast -c:a aac -b:a 256k b4k/B.mp4
ffmpeg -loglevel error -y -i b4k/p_3454_5.mp4 -i b4k/p_3454_6.mp4 -i b4k/p_3453_6.mp4 -ss 10.5 -t 4.75 -i raw/v3.mov -filter_complex "[0:v][1:v][2:v]concat=n=3:v=1:a=0,tpad=stop_mode=clone:stop_duration=0.5,trim=duration=4.75,setpts=PTS-STARTPTS,gblur=sigma=56,eq=brightness=0.04:saturation=0.8[v];[3:a]aresample=48000,afade=t=in:d=0.03,afade=t=out:st=4.7:d=0.05[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 14 -preset fast -c:a aac -b:a 256k b4k/C.mp4
echo "[3] cut $(date +%T)"
$PY build4k.py | head -1
cp b4k/cut.mp4 ../../remotion-composer/public/jirafik/v5-cut4k.mp4
echo "[4] matte $(date +%T)"
ffmpeg -loglevel error -y -i b4k/cut.mp4 -vf scale=1080:1920 -c:v libx264 -crf 16 -preset fast -an b4k/cut1080.mp4
$PY -I /home/user/OpenMontage/scripts/jirafik/matte.py b4k/cut1080.mp4 b4k/person.webm | tail -1
cp b4k/person.webm ../../remotion-composer/public/jirafik/v5-person120.webm
python3 - <<'PYEOF'
import json
p="/home/user/OpenMontage/remotion-composer/public/demo-props/"
d=json.load(open(p+"jirafik-ref5.json"))
d.update({"videoSrc":"jirafik/v5-cut4k.mp4","personSrc":"jirafik/v5-person120.webm","fps":120})
json.dump(d,open(p+"jirafik-ref5-4k120.json","w"),ensure_ascii=False,indent=1)
PYEOF
echo "[5] render $(date +%T)"
cd /home/user/OpenMontage/remotion-composer
npx remotion render JirafikVlog /home/user/OpenMontage/projects/vid5/b4k/render.mp4 --props=public/demo-props/jirafik-ref5-4k120.json --scale=2 --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell --crf=14 --concurrency=4 --log=error 2>&1 | grep -vi "webpack\|npm" | tail -3
cd /home/user/OpenMontage/projects/vid5
echo "[6] encode $(date +%T)"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 b4k/render.mp4); S=$(python3 -c "print($D-0.5)")
ffmpeg -loglevel error -y -i b4k/render.mp4 -vf "fade=t=out:st=$S:d=0.5" -af "afade=t=out:st=$S:d=0.5" -c:v libx265 -b:v 42M -maxrate 60M -bufsize 80M -x265-params log-level=error -preset medium -tag:v hvc1 -pix_fmt yuv420p -c:a aac -b:a 256k -movflags +faststart ref-vs-partner-4k120.mp4
B=$(python3 -c "print(int(28.3*8*1024*1024/$D-192000))")
ffmpeg -loglevel error -y -i ref-vs-partner-4k120.mp4 -vf "scale=1080:1920:flags=lanczos,fps=60" -c:v libx265 -b:v $B -x265-params pass=1:log-level=error -tag:v hvc1 -an -f null /dev/null
ffmpeg -loglevel error -y -i ref-vs-partner-4k120.mp4 -vf "scale=1080:1920:flags=lanczos,fps=60" -c:v libx265 -b:v $B -x265-params pass=2:log-level=error -tag:v hvc1 -c:a aac -b:a 192k -movflags +faststart ref-vs-partner-1080p60.mp4
ls -la ref-vs-partner-4k120.mp4 ref-vs-partner-1080p60.mp4
echo "DONE $(date +%T)"
