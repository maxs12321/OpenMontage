# HDR YouTube master: cards + subtitles drawn on a transparent 4K layer, converted sRGB -> HLG (npl 600, like the vertical
# videos) and laid over the untouched 10-bit HLG cut. Usage: final.py out.mp4 [start dur] (start/dur = short test)
import json, subprocess, sys
S=json.load(open("b/cards.json")); total=json.load(open("b/cutlist.json"))["total"]
out=sys.argv[1]; T0=float(sys.argv[2]) if len(sys.argv)>2 else 0; DUR=float(sys.argv[3]) if len(sys.argv)>3 else total
ins=["-ss",f"{T0:.3f}","-t",f"{DUR:.3f}","-i","b/cut.mp4","-f","lavfi","-i",f"color=c=black@0.0:s=3840x2160:r=60:d={DUR:.3f},format=rgba"]
fl=["[1:v]format=rgba[b0]"]; v="b0"; n=2
for k,(p,a,b,fi,fo,kind) in enumerate(S):
    b=min(b,total+0.5); a-=T0; b-=T0
    if b<=0 or a>=DUR: continue
    d=max(0.3,b-a)
    ins+=["-loop","1","-framerate","60","-t",f"{d:.3f}","-i",p]
    f=f"[{n}:v]format=rgba"
    if fi: f+=",fade=t=in:st=0:d=0.3:alpha=1"
    if fo: f+=f",fade=t=out:st={d-0.3:.3f}:d=0.3:alpha=1"
    f+=f",setpts=PTS+{max(a,0)-min(a,0)*0:.3f}/TB[c{k}]" if a>=0 else f",trim=start={-a:.3f},setpts=PTS-STARTPTS[c{k}]"
    fl.append(f); fl.append(f"[{v}][c{k}]overlay=0:0:eof_action=pass:format=auto[o{k}]"); v=f"o{k}"; n+=1
fl.append(f"[{v}]setpts=PTS+{T0:.3f}/TB,subtitles=b/subs.ass:fontsdir=/root/.fonts:alpha=1,setpts=PTS-STARTPTS,split[oc][oa]")
fl.append("[oc]format=gbrpf32le,zscale=tin=iec61966-2-1:pin=bt709:t=arib-std-b67:p=bt2020:npl=600,zscale=m=bt2020nc:r=tv,format=yuv420p10le[occ]")
fl.append("[oa]alphaextract,format=gray[oaa]")
fl.append("[occ][oaa]alphamerge,format=yuva420p10le[ov]")
fl.append("[0:v]format=yuv420p10le[v0]")
fl.append("[v0][ov]overlay=format=yuv420p10:eof_action=pass,format=yuv420p10le[vout]")
fl.append(f"[0:a]afade=t=out:st={max(0,total-T0-0.6):.3f}:d=0.6[aout]")
open("b/final_graph.txt","w").write(";\n".join(fl))
TAG=["-color_primaries","bt2020","-color_trc","arib-std-b67","-colorspace","bt2020nc"]
subprocess.run(["ffmpeg","-loglevel","error","-stats","-y"]+ins+["-filter_complex_script","b/final_graph.txt","-map","[vout]","-map","[aout]",
  "-c:v","libx265","-preset","fast","-pix_fmt","yuv420p10le","-tag:v","hvc1",
  "-x265-params","crf=17:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:keyint=120:log-level=error"]+TAG+
  ["-c:a","aac","-b:a","256k","-ar","48000","-movflags","+faststart","-t",f"{DUR:.3f}",out],check=True)
print("done",out)
