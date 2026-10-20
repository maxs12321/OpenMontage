import json, subprocess
d=json.load(open("timeline.json")); W=d["words"]; cuts=d["cuts"]
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
big=[]
for (t,n,lines,(f,k),_),(a,b),p in zip(spec,spans,probe):
    h=heads[str(p)]["headTop"]
    longest=max(len(l) for l in lines); size=int(min(470,int(1500/max(longest,2)))*k)
    blockH=len(lines)*size*f["lineHeight"]
    big.append({"start":a,"end":b,"lines":lines,"size":size,"top":max(60,int(h+170-blockH)),"align":"left","font":f})
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
bnds=[0.0]+cuts+[vd]
def shot_of(t):
    for i in range(len(bnds)-1):
        if bnds[i]<=t<bnds[i+1]: return [bnds[i],bnds[i+1]]
jr=[shot_of(t) for t in (at("возражение")["start"]-0.5, at("клиентов")["start"], cta["start"]+0.2)]
props={"videoSrc":"jirafik/v4-cut.mp4","videoDuration":vd,"cuts":cuts,"whooshAt":[],"emphasis":[],
 "words":W,"stickers":[],"inserts":[],"cta":cta,
 "hook":{"tag":"","line1":"Ниша РКО","line2":"простыми словами","until":2.4,"teaser":"что это и откуда деньги"},
 "hookStyle":"lower","captionStyle":"word","captionsFrom":2.4,"sfx":out,
 "endCard":{"seconds":0,"question":"","handles":[]},
 "motion":{"push":0.015,"jumpZoom":0.12,"jumpRanges":jr,"alternate":False,"punch":0,"blur":0,"flash":False,"emphasisZoom":0.05,"vignette":False},
 "plateTheme":"light","showProgress":False,"personSrc":"jirafik/v4-person.webm","bigWords":big}
json.dump(props,open("/home/user/OpenMontage/remotion-composer/public/demo-props/jirafik-rko4.json","w"),ensure_ascii=False,indent=1)
print("vd",vd,"jr",jr); print(big); print([(x["at"],x["src"].split('/')[-1]) for x in out])
