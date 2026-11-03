# HDR (HLG) delivery: video stays as the iPhone shot it (10-bit HLG, no tone mapping, no filters);
# only the transparent graphics are converted SDR->HLG and laid on top. Usage: hdr.py [seconds]
import json, subprocess, sys, os
LIM=float(sys.argv[1]) if len(sys.argv)>1 else None
FPS=60
exec(open("build.py").read().split("off=[];t=0")[0])          # same cut list as the SDR build
off=[];t=0
for a,b in pieces: off.append(t); t+=b-a
total=t
P=json.load(open("/home/user/OpenMontage/remotion-composer/public/demo-props/jirafik-rko2027-12.json"))
TAG=["-color_primaries","bt2020","-color_trc","arib-std-b67","-colorspace","bt2020nc"]
PR=["-c:v","libx264","-preset","fast","-crf","2","-pix_fmt","yuv422p10le"]+TAG   # near-lossless 10-bit, ~6x smaller than ProRes HQ
os.makedirs("b/hdr",exist_ok=True)
if LIM or not os.path.exists('b/hdr/cut.mov'):
  # 1) cut from the HLG source (10-bit, untouched colour), 60 fps, 1080x1920
  lst=[]
  for n,((a,b),o) in enumerate(zip(pieces,off)):
      if LIM and o>LIM+1: break
      out=f"b/hdr/p{n:03d}.mov"
      subprocess.run(["ffmpeg","-loglevel","error","-y","-ss",f"{a-0.002:.4f}","-i","raw/src.mov","-an","-vf","fps=60,scale=1080:1920:flags=lanczos",
                      "-frames:v",str(round((b-a)*FPS))]+PR+[out],check=True)
      lst.append(f"file 'p{n:03d}.mov'")
  open("b/hdr/list.txt","w").write("\n".join(lst)+"\n")
  subprocess.run(["ffmpeg","-loglevel","error","-y","-f","concat","-safe","0","-i","b/hdr/list.txt","-c","copy","b/hdr/cut.mov"],check=True)
# 2) centred close-ups (same ranges as the SDR edit): split at zoom changes, crop+scale the close parts
dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","b/hdr/cut.mov"]))
end=min(dur,LIM) if LIM else dur
# part transitions are done here on the 10-bit HLG frames (Remotion only draws the graphics): each transition window
# becomes its own segment, so it costs no extra encode generation
WIN={"whip":(0.15,0.15),"whipv":(0.15,0.15),"zoomin":(0.15,0.15),"dissolve":(0.0,0.4)}
tw=[(round(round((tr["at"]-WIN[tr["type"]][0])*FPS)/FPS,4),round(round((tr["at"]+WIN[tr["type"]][1])*FPS)/FPS,4),tr) for tr in P.get("transitions",[])]
pts=sorted({0.0,end}|{round(round(x*FPS)/FPS,4) for r in P["motion"]["jumpRanges"] for x in r[:2] if 0<x<end}|{x for a_,b_,_ in tw for x in (a_,b_) if 0<x<end})
def tfx(tr,D):
    e=f"(3*pow(t/{D},2)-2*pow(t/{D},3))"
    if tr["type"]=="whip":
        dx=tr.get("dir",1)
        return (f"split=3[w1][w2][w3];[w1][w2][w3]hstack=3,crop=1080:1920:x='1080+{dx}*1080*{e}':y=0,"
                f"gblur=sigma=22:sigmaV=0.6:enable='between(t,{D*0.2:.3f},{D*0.8:.3f})'")
    if tr["type"]=="whipv":
        dy=tr.get("dir",1)
        return (f"split=3[w1][w2][w3];[w1][w2][w3]vstack=3,crop=1080:1920:x=0:y='1920+{dy}*1920*{e}',"
                f"gblur=sigma=0.6:sigmaV=26:enable='between(t,{D*0.2:.3f},{D*0.8:.3f})'")
    if tr["type"]=="zoomin":
        z=f"(1+0.3*sin(PI*t/{D}))"
        return (f"scale=w='2*trunc(540*{z})':h='2*trunc(960*{z})':eval=frame:flags=bicubic,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,"
                f"gblur=sigma=7:enable='between(t,{D*0.25:.3f},{D*0.75:.3f})'")
    if tr["type"]=="dissolve":
        n=round(D*FPS)
        return (f"split[m][f];[f]trim=end_frame=1,loop=loop={n}:size=1,setpts=N/{FPS}/TB,gblur=sigma=14,format=yuva420p10le,"
                f"fade=t=out:st=0:d={D}:alpha=1[fr];[mm][fr]overlay=format=yuv420p10:eof_action=pass")

lst=[]
for k,(a,b) in enumerate(zip(pts,pts[1:])):
    mid=(a+b)/2; z=next((r[2] for r in P["motion"]["jumpRanges"] if r[0]<=mid<r[1]),0)
    s=1+z; cw=int(1080/s)//2*2; ch=int(1920/s)//2*2
    vf="null" if not z else f"crop={cw}:{ch}:{(1080-cw)//2}:{(1920-ch)//2},scale=1080:1920:flags=lanczos"
    trw=next((tr for a_,b_,tr in tw if a_<=mid<b_),None)
    if trw: vf=vf+","+tfx(trw,round(b-a,4))
    # dissolve: freeze the frame just BEFORE the window over the new part
    if trw and trw["type"]=="dissolve": a_ss=a-1/FPS
    else: a_ss=a
    out=f"b/hdr/z{k:03d}.mov"
    nf=round((b-a)*FPS)
    if trw and trw["type"]=="dissolve":
        vf=vf.replace("split[m][f];[f]trim=end_frame=1","split[m][f];[m]trim=start_frame=1,setpts=PTS-STARTPTS[mm];[f]trim=end_frame=1")
        subprocess.run(["ffmpeg","-loglevel","error","-y","-ss",f"{a_ss:.4f}","-i","b/hdr/cut.mov","-frames:v",str(nf),"-filter_complex","[0:v]"+vf]+PR+[out],check=True)
    else:
        subprocess.run(["ffmpeg","-loglevel","error","-y","-ss",f"{a:.4f}","-i","b/hdr/cut.mov","-frames:v",str(nf),"-filter_complex","[0:v]"+vf]+PR+[out],check=True)
    lst.append(f"file 'z{k:03d}.mov'")
open("b/hdr/zlist.txt","w").write("\n".join(lst)+"\n")
subprocess.run(["ffmpeg","-loglevel","error","-y","-f","concat","-safe","0","-i","b/hdr/zlist.txt","-c","copy","b/hdr/zoomed.mov"],check=True)
# 3) graphics: sRGB -> HLG BT.2020 (white at 203 nits, like iOS UI over HDR), overlay; person back on top of the big word
bw=P["bigWords"][0] if P.get("bigWords") else None
fl=["[1:v]format=rgba,split[oc][oa]","[oc]format=gbrpf32le,zscale=tin=iec61966-2-1:pin=bt709:t=arib-std-b67:p=bt2020:npl=600,zscale=m=bt2020nc:r=tv,format=yuv420p10le[occ]",
    "[oa]alphaextract,format=gray[oaa]","[occ][oaa]alphamerge,format=yuva420p10le[o]",
    "[0:v]format=yuv420p10le[b]","[b][o]overlay=format=yuv420p10:eof_action=pass[v1]"]
ins=["-i","b/hdr/zoomed.mov","-framerate","60","-i","b/ovl/element-%04d.png" if os.path.exists("b/ovl/element-0000.png") else "b/ovl/element-%03d.png"]
last="v1"
if bw and (not LIM or bw["start"]<end):
    ins+=["-c:v","libvpx-vp9","-i","b/person.webm","-i","b/hdr/zoomed.mov"]
    fl+=[f"[2:v]alphaextract,format=gray,scale=1080:1920[m]",f"[3:v]format=yuv420p10le[pf]","[pf][m]alphamerge,format=yuva420p10le[p]",
         f"[v1][p]overlay=format=yuv420p10:enable='between(t,{bw['start']},{bw['end']})'[v2]"]
    last="v2"
fl.append(f"[{last}]format=yuv420p10le[vout]")
out="b/hdr_test.mp4" if LIM else "b/hdr_final_video.mp4"
cmd=["ffmpeg","-loglevel","error","-y"]+ins+["-i","b/final_audio_n.wav","-filter_complex",";".join(fl),"-map","[vout]","-map",f"{ins.count('-i')}:a",
     "-t",f"{end:.3f}","-c:v","libx265","-preset","slow","-pix_fmt","yuv420p10le",
     "-x265-params","crf=14:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:hdr10=0",
     "-tag:v","hvc1"]+TAG+["-c:a","aac","-b:a","256k","-ar","48000","-movflags","+faststart",out]
subprocess.run(cmd,check=True); print("done",out)
