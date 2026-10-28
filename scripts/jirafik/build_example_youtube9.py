# YouTube 16:9 cut: drop pauses and fillers, calm wide/close alternation, audio stitched with crossfades
import json, subprocess, os, wave, numpy as np
SRC="b/full60c.mp4"          # colour-graded 1080p60 with the mic LED removed
END=592.1; SR=48000; FPS=60
g=[w for w in json.load(open("b/full_g.json")) if w["word"].strip()]
wseg=[(s["start"],s["end"]) for s in json.load(open("b/full_w.json"))]
DROP=[(111.30,112.10),(275.85,276.10)]          # "у..." and "ээ"
# keep speech, squeeze pauses: a gap over 0.6 s between words is cut down to ~0.4 s
ws_=[w for w in g if not any(d0<=w["start"]<d1 for d0,d1 in DROP)]
cut=[];cur=[max(0,ws_[0]["start"]-0.15),ws_[0]["end"]]
for w0,w1 in zip(ws_,ws_[1:]):
    gap=w1["start"]-w0["end"]
    if gap>0.6:
        cut.append((cur[0],w0["end"]+0.2)); cur=[w1["start"]-0.2,w1["end"]]
    else: cur[1]=w1["end"]
cut.append((cur[0],min(END,cur[1]+0.3)))
# extra split points (no time removed) at natural pauses so the framing can change there
SPL=[(w0["end"]+w1["start"])/2 for w0,w1 in zip(ws_,ws_[1:]) if 0.25<=w1["start"]-w0["end"]<=0.6]
SRCA=np.frombuffer(subprocess.run(["ffmpeg","-loglevel","error","-i","b/full60.mp4","-vn","-ac","1","-ar",str(SR),"-af","highpass=f=80:poles=2,adeclick","-f","s16le","-"],capture_output=True,check=True).stdout,np.int16).astype(np.float32)/32768
def quietest(t0,t1):
    ts=np.arange(t0,t1,0.01)
    if not len(ts): return (t0+t1)/2
    e=[np.mean(SRCA[int(t*SR):int(t*SR)+480]**2) for t in ts]
    return float(ts[int(np.argmin(e))])+0.005
for k in range(len(cut)-1):
    b,a2=cut[k][1],cut[k+1][0]
    nb=quietest(b-0.1,min(a2,b+0.2)); na=quietest(max(nb,a2-0.2),a2+0.08)
    if na>nb: cut[k]=(cut[k][0],nb); cut[k+1]=(na,cut[k+1][1])
sp=[]
for a,b in cut:
    pts=[a]+[x for x in SPL if a+2<x<b-2]+[b]
    sp+=list(zip(pts,pts[1:]))
pieces=[(round(a*FPS)/FPS,round(b*FPS)/FPS) for a,b in sp]
pieces=[p for p in pieces if p[1]-p[0]>=0.2]
off=[];t=0
for a,b in pieces: off.append(t); t+=b-a
total=t
# framing: switch between wide and a centred, top-anchored 1.2x close-up at a cut, roughly every 15-25 s
Z=1.2; cw,ch=int(1920/Z)//2*2,int(1080/Z)//2*2
frame=[];state=0;since=0
for k,(a,b) in enumerate(pieces):
    if k and since>=15: state^=1; since=0
    frame.append(state); since+=b-a
json.dump({"pieces":pieces,"off":off,"frame":frame,"total":total},open("b/cutlist.json","w"))
os.makedirs("b/pc",exist_ok=True); lst=[]
for n,((a,b),fr) in enumerate(zip(pieces,frame)):
    d=b-a; out=f"b/pc/p{n:03d}.mp4"
    vf="setpts=PTS-STARTPTS"+(f",crop={cw}:{ch}:{(1920-cw)//2}:0,scale=1920:1080:flags=lanczos,unsharp=5:5:0.4" if fr else "")
    # the LED pass was finished in two files: full60c up to 446 s, full60d from 420 s on
    src,ss=(SRC,a) if b<=446.0 else ("b/full60d.mp4",a-420.0)
    subprocess.run(["ffmpeg","-loglevel","error","-y","-ss",f"{ss-0.002:.4f}","-i",src,"-frames:v",str(round(d*FPS)),"-an","-vf",vf,"-r","60",
                    "-c:v","libx264","-crf","14","-preset","fast","-pix_fmt","yuv420p",out],check=True)
    lst.append(f"file 'pc/p{n:03d}.mp4'")
open("b/list.txt","w").write("\n".join(lst)+"\n")
H=0.02; outa=np.zeros(int((total+0.1)*SR),np.float32)
for k,((a,b),o) in enumerate(zip(pieces,off)):
    p=0 if k==0 else H; q=0 if k==len(pieces)-1 else H
    seg=SRCA[int(round((a-p)*SR)):int(round((b+q)*SR))].copy(); n=len(seg)
    if p: seg[:int(2*p*SR)]*=np.linspace(0,1,int(2*p*SR))
    if q: seg[n-int(2*q*SR):]*=np.linspace(1,0,int(2*q*SR))
    st=int(round((o-p)*SR)); outa[st:st+n]+=seg[:len(outa)-st]
with wave.open("b/cut_audio.wav","wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(outa,-1,1)*32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg","-loglevel","error","-y","-f","concat","-safe","0","-i","b/list.txt","-i","b/cut_audio.wav","-map","0:v","-map","1:a","-c:v","copy",
  "-af","loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000","-ac","2","-c:a","aac","-b:a","256k","-shortest","b/cut.mp4"],check=True)
print("pieces",len(pieces),"total",round(total,2),"removed",round(END-total,1),"s; close-ups",sum(frame))
