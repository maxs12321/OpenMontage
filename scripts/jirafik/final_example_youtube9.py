# overlay cards + subtitles + soft section whooshes onto the cut, encode for YouTube
import json, subprocess, sys
S=json.load(open("b/cards.json")); total=json.load(open("b/cutlist.json"))["total"]
J="/home/user/OpenMontage/remotion-composer/public/jirafik/"
ins=["-i","b/cut.mp4"]; fl=[]; v="0:v"
for k,(p,a,b,fi,fo,kind) in enumerate(S):
    b=min(b,total+0.5); d=max(0.3,b-a)
    ins+=["-loop","1","-framerate","60","-t",f"{d:.3f}","-i",p]
    f=f"[{k+1}:v]format=rgba"
    if fi: f+=",fade=t=in:st=0:d=0.3:alpha=1"
    if fo: f+=f",fade=t=out:st={d-0.3:.3f}:d=0.3:alpha=1"
    f+=f",setpts=PTS+{a:.3f}/TB[c{k}]"
    fl.append(f); fl.append(f"[{v}][c{k}]overlay=0:0:eof_action=pass[v{k}]"); v=f"v{k}"
fl.append(f"[{v}]subtitles=b/subs.ass:fontsdir=/root/.fonts,format=yuv420p[vout]")
chips=[a for (p,a,b,fi,fo,kind) in S if kind=="chip"]
n0=len(S)+1
for i,a in enumerate(chips):
    ins+=["-i",J+"sfx2-whoosh-short.wav"]; ms=int(a*1000)
    fl.append(f"[{n0+i}:a]aformat=channel_layouts=stereo,volume=0.22,adelay={ms}|{ms}[s{i}]")
fl.append("[0:a]"+"".join(f"[s{i}]" for i in range(len(chips)))+f"amix=inputs={len(chips)+1}:normalize=0:duration=first,afade=t=out:st={total-0.6:.3f}:d=0.6[aout]")
open("b/final_graph.txt","w").write(";\n".join(fl))
out=sys.argv[1] if len(sys.argv)>1 else "b/final.mp4"
subprocess.run(["ffmpeg","-loglevel","error","-y"]+ins+["-filter_complex_script","b/final_graph.txt","-map","[vout]","-map","[aout]",
  "-c:v","libx264","-profile:v","high","-preset","slow","-crf","17","-maxrate","14M","-bufsize","28M","-g","120","-pix_fmt","yuv420p",
  "-c:a","aac","-b:a","256k","-ar","48000","-movflags","+faststart","-t",f"{total:.3f}",out],check=True)
print("done",out)
