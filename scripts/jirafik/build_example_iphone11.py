import json, subprocess
g=[dict(w,word=w["word"].strip()) for w in json.load(open("b/full_g.json"))]
wseg=[(s["start"],s["end"]) for s in json.load(open("b/full_w.json"))]
# exact first frames of each shot change (60 fps grid)
DARK=[]   # one face take
END=43.381
fix={0:"iPhone",1:"18",2:"Pro —",4:"2",5:"человека,",6:"а не",7:"2",10:"смене.",11:"Для",17:"ногах,",22:"2",23:"разговора.",24:"За",30:"53 000 ₽.",31:"",32:"",33:"",34:"Нахожу",35:"второго —",40:"106 000 ₽.",41:"",42:"",43:"Вот",50:"платит.",51:"Что",62:"банках?",63:"Сейчас",64:"расскажу.",65:"Открывает",67:"бизнес-счета",68:"",72:"дела,",75:"банков,",86:"корзине.",87:"Например,",95:"работы,",99:"встанет.",100:"Более",101:"подробно:",104:"РКО",106:"словами,",110:"банки —",114:"закреплённых",117:"профиле.",118:"А",121:"так же —",129:"всё",131:"нуля.",132:"Так",137:"Telegram",138:"канал."}
KEY={0,4,23,30,40,46,83,104,125,137}
# keep intervals: whisper segments, extended to cover the words they hold, gaps trimmed
keep=[];cur=[max(0,g[0]["start"]-0.1),g[0]["end"]]
for w0,w1 in zip(g,g[1:]):
    if w1["start"]-w0["end"]>0.35: keep.append((cur[0],w0["end"]+0.15)); cur=[w1["start"]-0.12,w1["end"]]
    else: cur[1]=w1["end"]
keep.append((cur[0],min(END,cur[1]+0.3)))
keep[0]=(0.0,keep[0][1])
# split at shot boundaries so each piece is all-face or all-dark
cuts_src=sorted([x for d in DARK for x in d])
pieces=[]
for a,b in keep:
    pts=[a]+[c for c in cuts_src if a<c<b]+[b]
    # snap to the 60 fps grid so piece lengths are whole frames and the concat doesn't drift
    pts=[round(x*60)/60 for x in pts]
    for i in range(len(pts)-1):
        if pts[i+1]>pts[i]: pieces.append((pts[i],pts[i+1]))
def dark(a,b): return any(d0-0.01<=a and b<=d1+0.01 for d0,d1 in DARK)
# move every pause cut into the quietest 10 ms of the pause (Whisper segment edges often land on a breath
# or the tail of a syllable, which sounds like a glitch when cut)
import numpy as np
SR=48000
# low rumble (AC/street, 40-200 Hz) under the voice: phone speakers hide it, headphones don't, and it jumps at every cut
SRC=np.frombuffer(subprocess.run(["ffmpeg","-loglevel","error","-i","b/full60n.mp4","-vn","-ac","1","-ar",str(SR),"-af","highpass=f=80:poles=2,adeclick","-f","s16le","-"],capture_output=True,check=True).stdout,np.int16).astype(np.float32)/32768
def quietest(t0,t1):
    ts=np.arange(t0,t1,0.01)
    if not len(ts): return (t0+t1)/2
    e=[np.mean(SRC[int(t*SR):int(t*SR)+480]**2) for t in ts]
    return float(ts[int(np.argmin(e))])+0.005
ref=[list(p) for p in pieces]
for k in range(len(ref)-1):
    b,a2=ref[k][1],ref[k+1][0]
    if a2-b<0.02: continue   # shot boundary inside continuous audio
    nb=round(quietest(b-0.12,min(a2,b+0.25))*60)/60
    na=round(quietest(max(nb,a2-0.25),a2+0.1)*60)/60
    if na>nb and nb>ref[k][0]+0.2 and na<ref[k+1][1]-0.2: ref[k][1],ref[k+1][0]=nb,na
pieces=[tuple(p) for p in ref]
off=[];t=0
for a,b in pieces: off.append(t); t+=b-a
total=t
def mp(x):
    for (a,b),o in zip(pieces,off):
        if a<=x<b+0.001: return o+(x-a)
words=[]
for i,w in enumerate(g):
    txt=fix.get(i,w["word"])
    if txt=="": continue
    s=mp(w["start"])
    if s is None: continue
    j=i+1
    while j<len(g) and fix.get(j,"x")=="": j+=1
    nxt=mp(g[j]["start"]) if j<len(g) and mp(g[j]["start"]) is not None else s+0.5
    words.append({"text":txt,"start":round(s,3),"end":round(min(nxt,s+0.9),3),**({"key":True} if i in KEY else {})})
# shots in cut time
shots=[]
for (a,b),o in zip(pieces,off):
    kind="dark" if dark(a,b) else "face"
    if shots and shots[-1][2]==kind and abs(shots[-1][1]-o)<1e-6: shots[-1][1]=o+b-a
    else: shots.append([o,o+b-a,kind])
# background for dark pieces: the third face shot (39.95-52.7), blurred, played on from piece to piece
BG=(39.95,52.7)
import os
os.makedirs("b/pc",exist_ok=True)
lst=[];bgp=BG[0]
for n,(a,b) in enumerate(pieces):
    d=b-a; out=f"b/pc/p{n:03d}.mp4"
    if dark(a,b):
        s0=bgp
        if s0+d>BG[1]: s0=BG[0]
        bgp=s0+d
        cmd=["ffmpeg","-loglevel","error","-y","-ss",str(s0),"-t",str(d),"-i","b/full60n.mp4","-ss",f"{a-0.002:.4f}","-t",str(d),"-i","b/full60n.mp4",
             "-filter_complex",f"[0:v]setpts=PTS-STARTPTS,gblur=sigma=30,eq=brightness=0.03:saturation=0.85,setsar=1[v];[1:a]asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d-0.03:.3f}:d=0.03[a]",
             "-map","[v]","-map","[a]"]
    else:
        cmd=["ffmpeg","-loglevel","error","-y","-ss",f"{a-0.002:.4f}","-t",str(d),"-i","b/full60n.mp4",
             "-filter_complex",f"[0:v]setpts=PTS-STARTPTS,setsar=1[v];[0:a]asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d-0.03:.3f}:d=0.03[a]","-map","[v]","-map","[a]"]
    subprocess.run(cmd+["-frames:v",str(round(d*60)),"-r","60","-c:v","libx264","-crf","8","-preset","fast","-pix_fmt","yuv420p","-c:a","pcm_s16le","-ar","48000",out.replace(".mp4",".mov")],check=True)
    lst.append(f"file 'pc/p{n:03d}.mov'")
open("b/list.txt","w").write("\n".join(lst)+"\n")
# audio: stitch the pieces straight from the source with 40 ms linear crossfades centred on each cut,
# so the room tone never drops to silence between pieces (a fade-out/fade-in hole sounds like a click)
H=0.02
out=np.zeros(int((total+0.1)*SR),np.float32)
for k,((a,b),o) in enumerate(zip(pieces,off)):
    pre=0 if k==0 else H; post=0 if k==len(pieces)-1 else H
    seg=SRC[int(round((a-pre)*SR)):int(round((b+post)*SR))].copy()
    n=len(seg); fi=int(2*pre*SR); fo=int(2*post*SR)
    if fi: seg[:fi]*=np.linspace(0,1,fi)
    if fo: seg[n-fo:]*=np.linspace(1,0,fo)
    st=int(round((o-pre)*SR)); out[st:st+n]+=seg[:len(out)-st]
import wave
with wave.open("b/cut_audio.wav","wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(out,-1,1)*32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg","-loglevel","error","-y","-f","concat","-safe","0","-i","b/list.txt","-i","b/cut_audio.wav","-map","0:v","-map","1:a","-c:v","copy","-af","loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000","-ac","2","-c:a","aac","-b:a","256k","-shortest","b/cut_rawn.mp4"],check=True)
subprocess.run(["ffmpeg","-loglevel","error","-y","-i","b/cut_rawn.mp4","-vf","tpad=stop_mode=clone:stop_duration=0.4","-af","apad=pad_dur=0.4","-c:v","libx264","-crf","8","-preset","fast","-pix_fmt","yuv420p","-c:a","aac","-b:a","256k","-t",str(round(total+0.4,3)),"b/cut_n.mp4"],check=True)
json.dump({"total":round(total,3),"cuts":[round(o,3) for o in off[1:]],"shots":[[round(a,3),round(b,3),k] for a,b,k in shots],"words":words},open("timeline_n.json","w"),ensure_ascii=False,indent=1)
print("total",round(total,2)); print("shots",[[round(a,2),round(b,2),k] for a,b,k in shots])
print(" ".join(f'{w["text"]}{"*" if w.get("key") else ""}@{w["start"]}' for w in words))
