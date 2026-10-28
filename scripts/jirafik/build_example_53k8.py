import json, subprocess
g=[dict(w,word=w["word"].strip()) for w in json.load(open("b/full_g.json"))]
wseg=[(s["start"],s["end"]) for s in json.load(open("b/full_w.json"))]
# exact first frames of each shot change (60 fps grid)
DARK=[]   # one face take, no voice-over pieces
END=71.49
fix={0:"Шесть",4:"53 000 ₽",5:"",6:"",7:"",10:"человека.",11:"При",19:"копейки.",20:"Читаю",24:"шестому.",25:"Последний",27:"интересный.",28:"Первый",31:"Альфа-Банк",32:"",34:"14 000 ₽",35:"",36:"",40:"счёта.",41:"Второй",43:"счёту",46:"идёт",47:"Т-Банк,",48:"",52:"10 000",54:"20 000 ₽.",55:"",56:"",57:"Но",62:"регистрации.",63:"Следующий",67:"Ozon Банк,",68:"",71:"8 000 ₽",72:"",73:"",77:"счёта.",78:"Но",83:"активен.",84:"Четвёртый",89:"ВТБ,",93:"8 000 ₽.",94:"",95:"",96:"Здесь",100:"счёт",102:"5 000 ₽",103:"",105:"сутки.",106:"И",112:"активен.",113:"Далее",116:"идёт",117:"ПСБ,",120:"9 000 ₽",121:"",122:"",125:"счёта",132:"690 ₽.",133:"",134:"",135:"Но",144:"4",145:"месяцев.",146:"И",150:"Сбер,",153:"4 000 ₽.",154:"",155:"",156:"Но",160:"приглашённый",167:"3 000 ₽.",168:"",169:"Также",175:"почему-то",176:"",184:"ИП",186:"НПД.",187:"А",197:"в своём",199:"обучении,",204:"Telegram",205:"канал."}
KEY={4,19,31,34,47,54,67,71,89,93,117,120,150,153,167,184,186,198,204}
# keep intervals: whisper segments, extended to cover the words they hold, gaps trimmed
keep=[]
for a,b in wseg:
    inside=[w for w in g if a-0.4<=w["start"]<=b+0.3]
    if inside: a=min(a,inside[0]["start"]); b=max(b,inside[-1]["start"]+0.42)
    a=max(0,a-0.1); b=min(END,b+0.12)
    if keep and a<=keep[-1][1]+0.05: keep[-1]=(keep[-1][0],b)
    else: keep.append((a,b))
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
SRC=np.frombuffer(subprocess.run(["ffmpeg","-loglevel","error","-i","b/full60.mp4","-vn","-ac","1","-ar",str(SR),"-af","highpass=f=100:poles=2,highpass=f=100:poles=2","-f","s16le","-"],capture_output=True,check=True).stdout,np.int16).astype(np.float32)/32768
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
        cmd=["ffmpeg","-loglevel","error","-y","-ss",str(s0),"-t",str(d),"-i","b/full60.mp4","-ss",f"{a-0.002:.4f}","-t",str(d),"-i","b/full60.mp4",
             "-filter_complex",f"[0:v]setpts=PTS-STARTPTS,gblur=sigma=30,eq=brightness=0.03:saturation=0.85,setsar=1[v];[1:a]asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d-0.03:.3f}:d=0.03[a]",
             "-map","[v]","-map","[a]"]
    else:
        cmd=["ffmpeg","-loglevel","error","-y","-ss",f"{a-0.002:.4f}","-t",str(d),"-i","b/full60.mp4",
             "-filter_complex",f"[0:v]setpts=PTS-STARTPTS,setsar=1[v];[0:a]asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d-0.03:.3f}:d=0.03[a]","-map","[v]","-map","[a]"]
    subprocess.run(cmd+["-frames:v",str(round(d*60)),"-r","60","-c:v","libx264","-crf","12","-preset","fast","-pix_fmt","yuv420p","-c:a","pcm_s16le","-ar","48000",out.replace(".mp4",".mov")],check=True)
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
subprocess.run(["ffmpeg","-loglevel","error","-y","-f","concat","-safe","0","-i","b/list.txt","-i","b/cut_audio.wav","-map","0:v","-map","1:a","-c:v","copy","-af","loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000","-ac","2","-c:a","aac","-b:a","256k","-shortest","b/cut_raw.mp4"],check=True)
subprocess.run(["ffmpeg","-loglevel","error","-y","-i","b/cut_raw.mp4","-vf","tpad=stop_mode=clone:stop_duration=0.4","-af","apad=pad_dur=0.4","-c:v","libx264","-crf","12","-preset","fast","-pix_fmt","yuv420p","-c:a","aac","-b:a","256k","-t",str(round(total+0.4,3)),"b/cut.mp4"],check=True)
json.dump({"total":round(total,3),"cuts":[round(o,3) for o in off[1:]],"shots":[[round(a,3),round(b,3),k] for a,b,k in shots],"words":words},open("timeline.json","w"),ensure_ascii=False,indent=1)
print("total",round(total,2)); print("shots",[[round(a,2),round(b,2),k] for a,b,k in shots])
print(" ".join(f'{w["text"]}{"*" if w.get("key") else ""}@{w["start"]}' for w in words))
