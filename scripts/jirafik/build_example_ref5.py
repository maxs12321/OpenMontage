import json, subprocess
# (file, src_start, src_end, words_json, words_from)
SEG=[("build/P.mp4",0.0,2.734,"build/P_g.json",0.0),
     ("build/A.mp4",0.12,7.53,"build/A_g.json",0.0),
     ("build/B.mp4",0.0,7.167,"raw/v2_giga.json",13.0),
     ("build/C.mp4",0.0,4.767,"raw/v3_giga.json",10.5),
     ("build/D.mp4",0.08,6.57,"build/D_g.json",0.0)]
DISP=[None,
 "Многие заходят в РКО так: берут реферальную ссылку с приложения банка, кидают её друзьям, по итогу получают копейки и срезы по заявкам.".split(),
 "Настоящая ниша — работа через партнёрские сети: это площадки, где собраны офферы десятков банков сразу, с отдельными ставками за клиента.".replace("— ","").split(),
 "Одна и та же заявка может принести тебе в разы меньше, просто потому что ты отправил её не туда.".split(),
 "Какие партнёрские сети мы используем и как ими правильно пользоваться — рассказываю в своём бесплатном обучении. Поэтому жду тебя в своём Telegram- канале.".replace("— ","").split()]
KEYS={1:{3,6,17},2:{4,10,16},3:{10,18},4:{13,20}}
words=[]; off=0; bounds=[]
for k,(f,a,b,wj,wf) in enumerate(SEG):
    g=[w for w in json.load(open(wj)) if w["start"]>=wf-0.05]
    if DISP[k] is not None:
        assert len(g)==len(DISP[k]),(k,len(g),len(DISP[k]),[w["word"] for w in g])
        for i,w in enumerate(g):
            s=off+(w["start"]-wf)-a
            nxt=(g[i+1]["start"]-wf-a+off) if i+1<len(g) else s+0.5
            words.append({"text":DISP[k][i],"start":round(s,3),"end":round(min(nxt,s+0.9),3),**({"key":True} if i in KEYS.get(k,()) else {})})
    off+=b-a; bounds.append(round(off,3))
total=off
cuts=bounds[:-1]
fc=[];inp=[]
for k,(f,a,b,_,_) in enumerate(SEG):
    inp+=["-i",f]
    fc.append(f"[{k}:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30,setsar=1[v{k}];[{k}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={b-a-0.03:.3f}:d=0.03[a{k}]")
n=len(SEG)
fc.append("".join(f"[v{i}][a{i}]" for i in range(n))+f"concat=n={n}:v=1:a=1[vc][ac]")
fc.append("[vc]tpad=stop_mode=clone:stop_duration=0.4[vo];[ac]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,apad=pad_dur=0.4[ao]")
subprocess.run(["ffmpeg","-loglevel","error","-y"]+inp+["-filter_complex",";".join(fc),"-map","[vo]","-map","[ao]","-c:v","libx264","-crf","12","-preset","medium","-pix_fmt","yuv420p","-c:a","aac","-b:a","256k","-t",str(round(total+0.4,3)),"build/cut.mp4"],check=True)
json.dump({"total":round(total,3),"cuts":cuts,"words":words},open("timeline.json","w"),ensure_ascii=False,indent=1)
print("total",round(total,2),"cuts",cuts)
print(" ".join(f'{w["text"]}{"*" if w.get("key") else ""}@{w["start"]}' for w in words))
