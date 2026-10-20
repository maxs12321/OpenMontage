import json, subprocess
d=json.load(open("timeline.json")); W=d["words"]
SC=[2.233,12.667,17.7,22.633,29.3,43.333,46.233]          # real shot changes (ffmpeg scene detect on cut.mp4)
off=[];t_=0
for a_,b_ in d["segs"]: off.append(t_); t_+=b_-a_
cuts=sorted(set(SC+[round(o,3) for o in off[1:]])); cuts=[c for k,c in enumerate(cuts) if k==0 or c-cuts[k-1]>0.4]
# sentence starts capitalised
prev="."
for w in W:
    if prev[-1:] in ".?!:" and w["text"][:1].islower() and w["text"] not in ("а",): w["text"]=w["text"][0].upper()+w["text"][1:]
    prev=w["text"].rstrip(" —")
def at(txt,n=1):
    c=0
    for w in W:
        if w["text"].strip(".,:!?…—-").strip().lower()==txt.lower():
            c+=1
            if c==n: return w
    raise KeyError(txt)
vd=round(d["total"]-0.07,3)
# big words behind the speaker: entities only, where he is on camera
spec=[("ИП",1,["ИП"],({"family":"'Russo One', sans-serif","weight":400,"lineHeight":0.95},0.85),0.9),
      ("мотив",1,["МОТИВ","ТРАФИК"],({"family":"Unbounded, sans-serif","weight":900,"lineHeight":0.95},0.62),1.0)]
spans=[]
for t,n,lines,fk,extra in spec:
    w=at(t,n); spans.append((round(w["start"]-0.05,3),round(w["start"]+extra+0.45,3)))
probe=[round(a+0.25,2) for a,b in spans]
heads=json.loads(subprocess.check_output(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/headpos.py","build/person.webm",json.dumps(probe)]).decode())
from PIL import ImageFont
FF={"Russo One":("/root/.fonts/RussoOne-Regular.ttf",1.0),"Unbounded":("/root/.fonts/Unbounded-Variable.ttf",1.12)}
def width(text,fam,size):
    for k,(path,mul) in FF.items():
        if k in fam: return ImageFont.truetype(path,size).getlength(text)*mul
    return len(text)*size*0.6
big=[]
for (t,n,lines,(f,k),_),(a,b),p in zip(spec,spans,probe):
    h=heads[str(p)]["headTop"]
    size=300
    while max(width(l,f["family"],size) for l in lines)>740: size-=5
    blockH=len(lines)*size*f["lineHeight"]
    big.append({"start":a,"end":b,"lines":lines,"size":size,"top":max(260,int(h+110-blockH)),"align":"center","font":f})
cta={"start":at("так")["start"],"end":vd,"label":"Мотив-трафик и связки — в бесплатном обучении","handle":"@jirafiktrafik"}
J="jirafik/"; S=[]
def add(t,src,vol): S.append({"at":round(t,3),"src":J+src,"volume":vol})
add(0.0,"sfx2-appear.wav",0.4)                                  # hook
for b in big: add(b["start"],"sfx2-zoom.wav",0.35)             # big word flies in
PAIR={"scale":("sfx2-whoosh-short.wav",0.4),"type":("sfx2-typing-real.wav",0.35)}
plan=[("НПД",1,"type"),("заработок",1,"scale"),("оплата",1,"scale"),("клиентов",1,"scale")]
for t,n,an in plan:
    w=at(t,n); w["anim"]=an; add(w["start"]-0.02,*PAIR[an])
add(cta["start"],"sfx2-whoosh-short.wav",0.4)                  # CTA card scales in
S.sort(key=lambda x:x["at"]); out=[]
for x in S:
    if out and x["at"]-out[-1]["at"]<0.3: continue
    out.append(x)
FACE=[(SC[0],SC[1]),(SC[3],SC[4]),(SC[5],vd)]   # shots where he is on camera
gaps=[(W[i]["end"],W[i+1]["start"]) for i in range(len(W)-1)]
def snap(x):
    near=[c for c in cuts if abs(c-x)<1.2]
    if near: return min(near,key=lambda c:abs(c-x))
    cand=[(g1-g0,(g0+g1)/2) for g0,g1 in gaps if abs((g0+g1)/2-x)<1.2]
    return round(max(cand)[1],3) if cand else x
jr=[]; levels=[0,0.16,0,0.26]
for fa,fb in FACE:
    pts=[fa]; x=fa
    while fb-x>7:
        x=snap(x+5)
        for bw in big:   # never change angle while a big word is behind him
            if bw["start"]-0.2<x<bw["end"]+0.1: x=round(min(g1 for g0,g1 in gaps if g0>=bw["end"]),3)
        pts.append(x)
    pts.append(fb)
    for k in range(len(pts)-1):
        z=levels[k%4]
        if z: jr.append([round(pts[k],3),round(pts[k+1],3),z])
mids=[round((r[0]+r[1])/2,2) for r in jr]
hp=json.loads(subprocess.check_output(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/headpos.py","build/person.webm",json.dumps(mids)]).decode())
for r,m in zip(jr,mids):
    h=hp[str(m)]; r+= [round(100*(h["headTop"]+170)/1920,1), round(100*h["cx"]/1080,1)]
TR=[(SC[0],"zoomin"),(SC[1],"whip"),(SC[3],"whip"),(SC[4],"flash"),(SC[5],"whip")]
TS={"flash":("sfx3-camera-shutter.wav",0.4,-0.08),"whip":("sfx2-swipe.wav",0.55,-0.12),"zoomin":("sfx2-zoom.wav",0.4,-0.2)}
for at_,ty in TR:
    src,vol,off=TS[ty]; out.append({"at":round(at_+off,3),"src":J+src,"volume":vol})
out.sort(key=lambda x:x["at"])
transitions=[{"at":a_,"type":t_,"dir":[1,-1][k%2]} for k,(a_,t_) in enumerate(TR)]
props={"videoSrc":"jirafik/v4-cut.mp4","videoDuration":vd,"cuts":cuts,"whooshAt":[],"emphasis":[],
 "words":W,"stickers":[],"inserts":[],"cta":cta,
 "hook":{"tag":"","line1":"Ниша РКО","line2":"простыми словами","until":2.4,"teaser":"что это и откуда деньги"},
 "hookStyle":"lower","captionStyle":"word","captionsFrom":2.4,"sfx":out,
 "endCard":{"seconds":0,"question":"","handles":[]},
 "motion":{"push":0.015,"jumpZoom":0.12,"jumpRanges":jr,"alternate":False,"punch":0,"blur":0,"flash":False,"emphasisZoom":0.05,"vignette":False},
 "transitions":transitions,"plateTheme":"light","showProgress":False,"personSrc":"jirafik/v4-person.webm","bigWords":big}
json.dump(props,open("/home/user/OpenMontage/remotion-composer/public/demo-props/jirafik-rko4.json","w"),ensure_ascii=False,indent=1)
print("vd",vd); print("jr",jr); print("tr",transitions); print(big); print([(x["at"],x["src"].split('/')[-1]) for x in out])
