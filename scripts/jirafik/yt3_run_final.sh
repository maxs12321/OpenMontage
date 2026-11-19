# waits for the cut, then encodes the HDR master in two halves and joins them without re-encoding
cd /home/user/OpenMontage/projects/yt3
until grep -q "^exit" b/build.log; do sleep 30; done
grep -q "^exit 0" b/build.log || { echo BUILD_FAILED > b/final.status; exit 1; }
rm -rf b/pc
PY=/home/user/OpenMontage/.venv/bin/python
T=$(python3 -c "import json;print(json.load(open('b/cutlist.json'))['total'])")
H=$(python3 -c "print(round(round($T/2*60)/60,4))")
$PY final.py b/part1.mp4 0 $H > b/final1.log 2>&1 || { echo P1_FAILED > b/final.status; exit 1; }
$PY final.py b/part2.mp4 $H $(python3 -c "print($T-$H)") > b/final2.log 2>&1 || { echo P2_FAILED > b/final.status; exit 1; }
printf "file 'part1.mp4'\nfile 'part2.mp4'\n" > b/parts.txt
ffmpeg -loglevel error -y -f concat -safe 0 -i b/parts.txt -c copy -movflags +faststart -tag:v hvc1 b/final.mp4 && echo DONE > b/final.status || echo CONCAT_FAILED > b/final.status
