import json, subprocess
g=[dict(w,word=w["word"].strip()) for w in json.load(open("b/full_g.json"))]
wseg=[(s["start"],s["end"]) for s in json.load(open("b/full_w.json"))]
# exact first frames of each shot change (60 fps grid)
DARK=[(443/60,1185/60),(1627/60,2395/60),(3167/60,4091/60)]
END=78.86
fix={0:"Банки",3:"59 000 ₽",4:"",5:"",6:"",9:"клиента.",10:"При",18:"копейки.",19:"Сейчас",23:"работает.",24:"Ниша",26:"РКО —",27:"расчётно-",29:"обслуживание.",30:"Если",31:"просто —",33:"счёт",35:"бизнеса.",36:"Банкам",39:"клиенты,",44:"привлечённого.",45:"Это",48:"бюджет.",49:"Вместо",55:"телевизору,",62:"человека.",63:"Я",65:"человека,",68:"счёт,",72:"комиссию.",73:"Клиенту",77:"стоит.",78:"А",82:"цифре.",83:"Он",85:"ИП",87:"НПД.",88:"Это",89:"упрощённый",95:"отчётности.",96:"Дальше",100:"счёт,",102:"несколько.",103:"И",106:"навязывание.",107:"Предприниматели",115:"банке,",119:"блокировки,",121:"работы,",123:"операций.",124:"2–3",125:"",126:"счёта —",128:"практика.",129:"И",132:"таблица:",133:"Альфа-Банк,",134:"",135:"ВТБ,",136:"Т-Банк,",137:"",138:"ПСБ,",139:"Сбербанк,",140:"Озон,",141:"ну",143:"бонусом",147:"Билайна.",148:"В",151:"59 000 ₽.",152:"",153:"",154:"",155:"Это",157:"расчёт",158:"на бумаге —",159:"это",161:"открутка.",162:"И",169:"клиентов.",170:"РКО",171:"—",177:"клиентов,",181:"это",186:"продукты.",187:"Многие",192:"офферы,",197:"деньги,",201:"по",202:"3 000 ₽,",203:"",206:"ниша",208:"окупается,",210:"уходят.",211:"Также",215:"мотив-",216:"трафик,",222:"офферов",229:"клиента.",230:"Где",233:"офферы,",235:"такое",236:"мотив-",237:"трафик —",238:"рассказываю",240:"своём",242:"обучении.",243:"Ищи",244:"Telegram",246:"профиле."}
KEY={3,26,35,72,87,93,95,102,119,121,122,128,132,151,161,168,183,202,208,241,244}
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
subprocess.run(["ffmpeg","-loglevel","error","-y","-f","concat","-safe","0","-i","b/list.txt","-c:v","copy","-af","loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000","-c:a","aac","-b:a","256k","b/cut_raw.mp4"],check=True)
subprocess.run(["ffmpeg","-loglevel","error","-y","-i","b/cut_raw.mp4","-vf","tpad=stop_mode=clone:stop_duration=0.4","-af","apad=pad_dur=0.4","-c:v","libx264","-crf","12","-preset","fast","-pix_fmt","yuv420p","-c:a","aac","-b:a","256k","-t",str(round(total+0.4,3)),"b/cut.mp4"],check=True)
json.dump({"total":round(total,3),"cuts":[round(o,3) for o in off[1:]],"shots":[[round(a,3),round(b,3),k] for a,b,k in shots],"words":words},open("timeline.json","w"),ensure_ascii=False,indent=1)
print("total",round(total,2)); print("shots",[[round(a,2),round(b,2),k] for a,b,k in shots])
print(" ".join(f'{w["text"]}{"*" if w.get("key") else ""}@{w["start"]}' for w in words))
