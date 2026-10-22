import json, subprocess
from PIL import ImageFont
d=json.load(open("timeline.json")); W=d["words"]
SC=d["cuts"]                                   # P|A|B|C|D boundaries
def at(txt,n=1):
    c=0
    for w in W:
        if w["text"].strip(".,:!?…—-").strip().lower()==txt.lower():
            c+=1
            if c==n: return w
    raise KeyError(txt)
vd=round(d["total"]-0.07,3)
# big word behind him (A shot only; D ends with the Telegram card)
rw=at("реферальную")
a,b=round(rw["start"]-0.05,3),round(at("банка")["start"],3)
head=json.loads(subprocess.check_output(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/headpos.py","build/person.webm",json.dumps([round(a+0.25,2)])]).decode())[str(round(a+0.25,2))]["headTop"]
f={"family":"'Russo One', sans-serif","weight":400,"lineHeight":0.95}
lines=["РЕФ-","ССЫЛКА"]; size=300
while max(ImageFont.truetype("/root/.fonts/RussoOne-Regular.ttf",size).getlength(l) for l in lines)>740: size-=5
big=[{"start":a,"end":b,"lines":lines,"size":size,"top":max(260,int(head+45-len(lines)*size*0.95)),"align":"center","font":f}]
compare={"start":SC[2],"end":SC[3],"items":[
  {"at":round(SC[2]+0.12,3),"label":"Реф-ссылка в приложении Альфы","src":"jirafik/v5-bank-ref.jpg","value":"5 000 баллов"},
  {"at":round(at("разы")["start"]-0.1,3),"label":"Партнёрская сеть · Альфа-Банк","src":"jirafik/v5-partner-alfa.jpg","value":"14 000 ₽","count":14000,"suffix":" ₽","good":True}],
  "crossAt":round(at("не")["start"],3)}
cta={"start":at("Поэтому")["start"],"end":vd,"label":"Партнёрки и связки — в бесплатном обучении","handle":"@jirafiktrafik"}
J="jirafik/"; S=[]
def add(t,src,vol): S.append({"at":round(t,3),"src":J+src,"volume":vol})
add(0.0,"sfx2-appear.wav",0.4)                                 # title
add(big[0]["start"],"sfx2-zoom.wav",0.35)                      # big word flies in
TR=[(SC[0],"whip"),(SC[1],"whip"),(SC[2],"zoomin"),(SC[3],"whip")]
TS={"whip":("sfx2-swipe.wav",0.55,-0.12),"zoomin":("sfx2-zoom.wav",0.4,-0.2)}
for t_,ty in TR: src,vol,o=TS[ty]; add(t_+o,src,vol)
add(compare["items"][1]["at"]+0.13,"sfx2-gauge.wav",0.35)      # 14 000 counts up
add(compare["crossAt"],"sfx3-mouse-click.wav",0.5)             # bank option crossed out
add(cta["start"],"sfx2-whoosh-short.wav",0.4)                  # Telegram card scales in
S.sort(key=lambda x:x["at"])
transitions=[{"at":t_,"type":ty,"dir":[1,-1][k%2]} for k,(t_,ty) in enumerate(TR)]
# angle change on his shots, ~every 5 s, aimed at the face
gaps=[(W[i]["end"],W[i+1]["start"]) for i in range(len(W)-1)]
def gap_near(x):
    c=[((g1-g0),(g0+g1)/2) for g0,g1 in gaps if abs((g0+g1)/2-x)<1.2 and g1>g0]
    return round(max(c)[1],3) if c else x
jr=[]
for fa,fb in [(SC[0],SC[1]),(SC[3],vd)]:
    m=gap_near(fa+(fb-fa)/2)
    if m<b+0.1 and m>a-0.2: m=gap_near(b+0.6)
    jr.append([m,fb,0.18])
mids=[round((r[0]+r[1])/2,2) for r in jr]
hp=json.loads(subprocess.check_output(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/headpos.py","build/person.webm",json.dumps(mids)]).decode())
for r,mm in zip(jr,mids): h=hp[str(mm)]; r+=[round(100*(h["headTop"]+170)/1920,1),round(100*h["cx"]/1080,1)]
props={"videoSrc":"jirafik/v5-cut.mp4","videoDuration":vd,"cuts":[0.9,1.667]+SC+[],"whooshAt":[],"emphasis":[],
 "words":W,"stickers":[],"inserts":[],"cta":cta,"compare":compare,
 "hook":{"tag":"","line1":"Реферальная ссылка банка","line2":"vs партнёрская сеть","until":SC[0],"teaser":"","size":96,"line2At":at("против")["start"] if any(w["text"]=="против" for w in W) else 1.36},
 "hookStyle":"lower","captionStyle":"word","captionsFrom":SC[0],"sfx":S,
 "endCard":{"seconds":0,"question":"","handles":[]},
 "motion":{"push":0.015,"jumpZoom":0.12,"jumpRanges":jr,"alternate":False,"punch":0,"blur":0,"flash":False,"emphasisZoom":0.05,"vignette":False},
 "transitions":transitions,"plateTheme":"light","showProgress":False,"personSrc":"jirafik/v5-person.webm","bigWords":big}
json.dump(props,open("/home/user/OpenMontage/remotion-composer/public/demo-props/jirafik-ref5.json","w"),ensure_ascii=False,indent=1)
print("vd",vd,"jr",jr); print(big); print(compare); print([(x["at"],x["src"].split('/')[-1]) for x in S])
