import json, subprocess
# (file, src_a, src_b, giga json, display tokens or None, key token idx)
G={k:[dict(w,word=w["word"].strip()) for w in json.load(open(f"b/{k}_g.json"))] for k in ["pv","A","Bv","C","D"]}
# (file, a, b, [(giga key, src_from, src_to, offset_in_segment)])
SEG=[("b/pv.mp4",0.0,1.83,[("pv",0.0,1.83,0.0)]),
     ("b/A.mp4",0.0,4.35,[("A",0.0,4.35,0.0)]),
     ("b/B2.mp4",0.0,7.087,[("A",4.6,6.037,0.0),("Bv",0.0,5.65,1.437)]),
     ("b/C.mp4",0.0,4.388,[("C",0.0,4.388,0.0)]),
     ("b/D.mp4",0.0,6.014,[("D",0.0,6.014,0.0)])]
DISP={"pv":"Один клиент, несколько банков.".split(),"A":"Знаешь, почему опытные предприниматели используют не один счёт в банке, а два- три? Если один банк заблокирует".split(),
      "Bv":"операции или уйдёт на техработы, бизнес не встанет. Запасной счёт это просто страховка. А для тебя это значит:".split(),
      "C":"клиент может принести не одну выплату, а несколько, если ему это действительно нужно.".split(),
      "D":"Какие банки сочетать и в каком порядке подавать заявки, рассказываю в своём бесплатном обучении. Ищи Telegram в профиле.".split()}
KEYS={"pv":set(),"A":{16},"Bv":{4,12},"C":{7},"D":{1,12,15}}
for k in DISP: assert len(DISP[k])==len(G[k]),(k,len(DISP[k]),len(G[k]),[w["word"] for w in G[k]])
words=[]; off=0; bounds=[]
for f,a,b,srcs in SEG:
    for k,fa,fb,o in srcs:
        g=G[k]
        for i,w in enumerate(g):
            if not (fa-0.05<=w["start"]<fb): continue
            s=off+o+w["start"]-fa
            nxt=(off+o+g[i+1]["start"]-fa) if i+1<len(g) and g[i+1]["start"]<fb else s+0.5
            words.append({"text":DISP[k][i],"start":round(s,3),"end":round(min(nxt,s+0.9),3),**({"key":True} if i in KEYS[k] else {})})
    off+=b-a; bounds.append(round(off,3))
total=off
fc=[];inp=[]
for n,(f,a,b,_) in enumerate(SEG):
    inp+=["-i",f]
    fc.append(f"[{n}:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=60,setsar=1[v{n}];[{n}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={b-a-0.03:.3f}:d=0.03[a{n}]")
n=len(SEG)
fc.append("".join(f"[v{i}][a{i}]" for i in range(n))+f"concat=n={n}:v=1:a=1[vc][ac]")
fc.append("[vc]tpad=stop_mode=clone:stop_duration=0.4[vo];[ac]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,apad=pad_dur=0.4[ao]")
subprocess.run(["ffmpeg","-loglevel","error","-y"]+inp+["-filter_complex",";".join(fc),"-map","[vo]","-map","[ao]","-c:v","libx264","-crf","12","-preset","fast","-pix_fmt","yuv420p","-c:a","aac","-b:a","256k","-t",str(round(total+0.4,3)),"b/cut.mp4"],check=True)
# shot boundaries: P|A, A|B, B|C, C|D
json.dump({"total":round(total,3),"cuts":bounds[:-1],"words":words},open("timeline.json","w"),ensure_ascii=False,indent=1)
print("total",round(total,2),"cuts",bounds[:-1])
print(" ".join(f'{w["text"]}{"*" if w.get("key") else ""}@{w["start"]}' for w in words))
