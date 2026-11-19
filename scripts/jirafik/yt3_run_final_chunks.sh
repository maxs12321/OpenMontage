# encodes the HDR master in 8 resumable chunks (finished chunks have a .ok marker), then joins video and adds one continuous audio track
cd /home/user/OpenMontage/projects/yt3
PY=/home/user/OpenMontage/.venv/bin/python
T=$(python3 -c "import json;print(json.load(open('b/cutlist.json'))['total'])")
N=8; F=$(python3 -c "print(int(round($T*60)))"); C=$(( (F+N-1)/N ))
: > b/parts.txt
for i in $(seq 0 $((N-1))); do
  S=$(( i*C )); L=$(( F-S < C ? F-S : C ))
  P=b/p$i.mp4
  echo "file 'p$i.mp4'" >> b/parts.txt
  [ -f $P.ok ] && continue
  echo RUN $i > b/final.status
  $PY final.py $P $(python3 -c "print($S/60)") $(python3 -c "print($L/60)") > b/fp$i.log 2>&1 || { echo P${i}_FAILED > b/final.status; exit 1; }
  touch $P.ok
done
ffmpeg -loglevel error -y -f concat -safe 0 -i b/parts.txt -i b/cut.mp4 -map 0:v -map 1:a -c:v copy \
  -af "afade=t=out:st=$(python3 -c "print($T-0.6)"):d=0.6" -c:a aac -b:a 256k -ar 48000 -t $T \
  -movflags +faststart -tag:v hvc1 b/final.mp4 && echo DONE > b/final.status || echo CONCAT_FAILED > b/final.status
