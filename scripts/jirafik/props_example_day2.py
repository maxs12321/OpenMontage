import json, subprocess
d=json.load(open("timeline.json")); W=d["words"]; cuts=d["cuts"]
for w in W:   # he said «новый оффер РКО», not ПСБ
    if w["text"]=="ПСБ,": w["text"]="РКО,"
def at(txt,n=1):
    c=0
    for w in W:
        if w["text"].strip(".,:!?…—").strip().lower()==txt.lower():
            c+=1
            if c==n: return w
    raise KeyError(txt)
vd=round(d["total"]-0.07,3)
ins=[{"src":"jirafik/v2-ins-analytics.jpg","start":round(at("доходы")["start"]-0.15,3),"duration":2.3,"label":"Аналитика","width":900,"aspect":900/693}]
# one big word behind the speaker: the 5 blocked traffic sources (he is on camera here)
a=round(at("пять")["start"]-0.05,3); b=round(at("заблокированы")["start"]-0.05,3)
head=json.loads(subprocess.check_output(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/headpos.py","build/person.webm",json.dumps([round(a+0.25,2)])]).decode())[str(round(a+0.25,2))]["headTop"]
f={"family":"'Russo One', sans-serif","weight":400,"lineHeight":0.95}
# centred in the TikTok safe zone (width <= 740 px, not above 260 px), head slightly overlaps the bottom
from PIL import ImageFont
lines=["5 ИСТОЧ-","НИКОВ"]; size=300
while max(ImageFont.truetype("/root/.fonts/RussoOne-Regular.ttf",size).getlength(l) for l in lines)>740: size-=5
blockH=len(lines)*size*f["lineHeight"]
big=[{"start":a,"end":b,"lines":lines,"size":size,"top":max(260,int(head+45-blockH)),"align":"center","font":f}]
J="jirafik/"; S=[]
def add(t,src,vol): S.append({"at":round(t,3),"src":J+src,"volume":vol})
add(0.0,"sfx2-appear.wav",0.4); add(0.17,"sfx2-appear.wav",0.35)        # hook lines
add(a,"sfx2-zoom.wav",0.35)                                               # big word behind
add(ins[0]["start"],"sfx2-swipe.wav",0.5)                                 # screenshot slides in
# each key word: entry animation + the one sound that belongs to it (Ilya's SFX tutorial)
PAIR={"flicker":("sfx2-charge.wav",0.45),"type":("sfx2-typing-real.wav",0.35),"scale":("sfx2-whoosh-short.wav",0.4),
      "appear":("sfx2-appear.wav",0.4),"rotate":("sfx2-paper-turn.wav",0.35),"zoom":("sfx2-zoom.wav",0.35),"count":("sfx2-gauge.wav",0.3)}
# few events, one base pair (scale+whoosh) repeated; special pairs only 1-2 per video
plan=[("заблокированы",1,"flicker"),("РКО",1,"scale"),("РКО",3,"scale"),("продуктивный",1,"scale")]
for t,n,an in plan:
    w=at(t,n); w["anim"]=an; add(w["start"]-0.02,*PAIR[an])
S.sort(key=lambda x:x["at"]); out=[]
for x in S:
    if out and x["at"]-out[-1]["at"]<0.3: continue
    out.append(x)
bnds=[0.0]+cuts+[vd]
def shot_of(t):
    for i in range(len(bnds)-1):
        if bnds[i]<=t<bnds[i+1]: return [bnds[i],bnds[i+1]]
jr=[shot_of(t) for t in (at("отчётность")["start"], at("РКО",3)["start"], at("продуктивный")["start"])]
z=at("заблокированы"); p=at("РКО",3)
props={"videoSrc":"jirafik/v2-cut.mp4","videoDuration":vd,"cuts":cuts,"whooshAt":[],
 "emphasis":[{"start":z["start"],"end":z["end"]},{"start":p["start"],"end":p["end"]}],
 "words":W,"stickers":[],"inserts":ins,
 "hook":{"tag":"","line1":"День","line2":"арбитражника","until":2.3,"teaser":"когда всё пошло не по плану"},
 "hookStyle":"lower","captionStyle":"word","captionsFrom":2.3,"sfx":out,
 "endCard":{"seconds":0,"question":"","handles":[]},
 "motion":{"push":0.015,"jumpZoom":0.12,"jumpRanges":jr,"alternate":False,"punch":0,"blur":0,"flash":False,"emphasisZoom":0.05,"vignette":False},
 "plateTheme":"light","showProgress":False,"personSrc":"jirafik/v2-person.webm","bigWords":big}
json.dump(props,open("/home/user/OpenMontage/remotion-composer/public/demo-props/jirafik-day2.json","w"),ensure_ascii=False,indent=1)
print("vd",vd,"jr",jr,"big",big); print([(x["at"],x["src"].split('/')[-1]) for x in out])
