import json, subprocess
d=json.load(open("timeline.json")); W=d["words"]; segs=d["segs"]
# clip boundaries in master -> cut timeline
b=0; bounds=[]
for i in range(1,16):
    v=float(subprocess.check_output(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=duration","-of","csv=p=0",f"raw/c{i:02d}.mov"]).decode().strip().strip(","))
    a=float(subprocess.check_output(["ffprobe","-v","error","-select_streams","a","-show_entries","stream=duration","-of","csv=p=0",f"raw/c{i:02d}.mov"]).decode().strip())
    b+=min(v,a); bounds.append(b)
off=[];t=0
for a_,b_ in segs: off.append(t); t+=b_-a_
def mp(x):
    for (a_,b_),o in zip(segs,off):
        if a_<=x<b_: return o+(x-a_)
cuts=sorted(set([round(c,3) for c in d["cuts"]]+[round(mp(x),3) for x in bounds[:-1] if mp(x) is not None]))
cuts=[c for i,c in enumerate(cuts) if i==0 or c-cuts[i-1]>0.5]
def at(txt,n=1):
    c=0
    for w in W:
        if w["text"].strip(".,:!?…—").strip().lower()==txt.lower():
            c+=1
            if c==n: return w
    raise KeyError(txt)
vd=round(d["total"]-0.06,3)
chapters=[{"start":at("Первый в")["start"],"end":at("Второй")["start"]-0.05,"kicker":"№1","title":"Альфа-Банк","value":"14 000 ₽"},
          {"start":at("Второй")["start"],"end":at("И")["start"]+0.2,"kicker":"№2","title":"ПСБ","value":"9 000 ₽"},
          {"start":at("третий")["start"],"end":at("Получается")["start"]-0.05,"kicker":"№3","title":"Т-Банк","value":"10–20 тыс. ₽"}]
calc={"start":at("три",2)["start"]+0.3,"end":at("Но",2)["start"]+0.6,"parts":["14 000","9 000","20 000"],"total":"43 000 ₽"}
cta={"start":at("поэтому")["start"],"end":vd,"label":"Бесплатное обучение — в Telegram","handle":"@jirafiktrafik"}
def span(t,n=1,extra=0.7):
    w=at(t,n); return round(w["start"]-0.05,3), round(w["end"]+extra,3)
import subprocess as _sp
spec=[("Альфа-Банк",1,["АЛЬ","ФА"]),("ПСБ",1,["ПСБ"]),("Т-Банк",1,["Т-","БАНК"]),]
spans=[span(t,n) for t,n,_ in spec]
heads=json.loads(_sp.check_output(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/headpos.py","build/person.webm",json.dumps([round(a+0.25,2) for a,b in spans])]).decode())
big=[]
for (t,n,lines),(a,b) in zip(spec,spans):
    h=heads[str(round(a+0.25,2))]["headTop"]
    longest=max(len(l) for l in lines); size=min(470,int(1500/max(longest,2)))
    blockH=len(lines)*size*0.86
    big.append({"start":a,"end":b,"lines":lines,"size":size,"top":int(h+170-blockH),"align":"left"})
# --- SFX: each sound tied to what the text does, no two identical in a row ---
J="jirafik/"
S=[]
def add(t,src,vol): S.append({"at":round(t,3),"src":J+src,"volume":vol})
add(0.0,"sfx2-appear.wav",0.4); add(0.17,"sfx2-appear.wav",0.35)          # hook lines
for k,c in enumerate(chapters): add(c["start"],["sfx2-swipe.wav","sfx2-whoosh-short.wav"][k%2],0.6 if k%2==0 else 0.35)  # chip slides in
for b in big: add(b["start"],"sfx2-zoom.wav",0.35)                          # giant word behind
bigstarts=[b["start"] for b in big]
money=("₽","тысяч")
for w in W:
    if not w.get("key") or w["start"]<3.4 or w["start"]>vd-1: continue
    if any(abs(w["start"]-b)<0.4 for b in bigstarts): continue             # already has zoom
    t=w["start"]-0.02
    if any(m in w["text"] for m in money): add(t,"sfx2-gauge.wav",0.3)      # amounts: counter tick
    elif w["text"].startswith("НПД"): add(t,"sfx3-camera-click.wav",0.45)
    elif w["text"].startswith("платном"): add(t,"sfx2-charge.wav",0.4)
    elif w["text"].startswith("бесплатном"): add(t,"sfx2-appear.wav",0.35)
    elif w["text"].startswith("телеграм"): pass
    else: add(t,"sfx3-mouse-click.wav",0.4)
add(calc["start"],"sfx3-mac-typing.wav",0.3); add(calc["start"]+25/30,"sfx3-ding.wav",0.5)   # sum typed, total dings
add(cta["start"],"sfx2-paper-turn.wav",0.3)
S.sort(key=lambda x:x["at"]); out=[]
for x in S:
    if out and x["at"]-out[-1]["at"]<0.3: continue
    out.append(x)
emph=[{"start":at("соврал")["start"],"end":at("соврал")["end"]}]
props={"videoSrc":"jirafik/v3-cut.mp4","videoDuration":vd,"cuts":cuts,"whooshAt":[],"emphasis":emph,
 "words":W,"stickers":[],"inserts":[],"chapters":chapters,"calc":calc,"cta":cta,
 "hook":{"tag":"","line1":"3 банка","line2":"33 000 ₽","until":3.3,"teaser":"с одного клиента"},
 "hookStyle":"lower","captionStyle":"word","captionsFrom":3.3,"sfx":out,
 "endCard":{"seconds":0,"question":"","handles":[]},
 "motion":{"push":0.02,"jumpZoom":0.12,"alternate":False,"punch":0,"blur":0,"flash":False,"emphasisZoom":0.05,"vignette":False},
 "plateTheme":"light","showProgress":False,"personSrc":"jirafik/v3-person.webm","bigWords":big}
json.dump(props,open("/home/user/OpenMontage/remotion-composer/public/demo-props/jirafik-banks3.json","w"),ensure_ascii=False,indent=1)
print("vd",vd,"cuts",cuts); print([(round(x["at"],2),x["src"].split('/')[-1][:12]) for x in out])
