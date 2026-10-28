# swap the soundtrack for the clean source (no background music) keeping the exact same cut
import subprocess, numpy as np, wave
src=open("build.py").read()
pre=src.split("off=[];t=0")[0]          # words, pieces and quiet-point refinement (uses the old audio, so pieces stay identical)
exec(pre)
off=[];t=0
for a,b in pieces: off.append(t); t+=b-a
total=t
NEW=np.frombuffer(subprocess.run(["ffmpeg","-loglevel","error","-i","raw/src2.mov","-vn","-ac","1","-ar",str(SR),"-af","highpass=f=80:poles=2,adeclick","-f","s16le","-"],capture_output=True,check=True).stdout,np.int16).astype(np.float32)/32768
H=0.02
out=np.zeros(int((total+0.1)*SR),np.float32)
for k,((a,b),o) in enumerate(zip(pieces,off)):
    p=0 if k==0 else H; q=0 if k==len(pieces)-1 else H
    seg=NEW[int(round((a-p)*SR)):int(round((b+q)*SR))].copy(); n=len(seg)
    if p: seg[:int(2*p*SR)]*=np.linspace(0,1,int(2*p*SR))
    if q: seg[n-int(2*q*SR):]*=np.linspace(1,0,int(2*q*SR))
    st=int(round((o-p)*SR)); out[st:st+n]+=seg[:len(out)-st]
with wave.open("b/cut_audio2.wav","wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out,-1,1)*32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg","-loglevel","error","-y","-i","b/cut.mp4","-i","b/cut_audio2.wav","-map","0:v","-map","1:a","-c:v","copy",
  "-af","loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,apad","-ac","2","-c:a","aac","-b:a","256k","-t",str(round(total+0.4,3)),"b/cut2.mp4"],check=True)
print("total",round(total,3),"cuts",[round(o,3) for o in off[1:]])
