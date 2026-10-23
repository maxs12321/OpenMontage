import json, subprocess
from PIL import ImageFont
d=json.load(open("timeline.json")); W=d["words"]; C=d["cuts"]   # A|B, B|C, C|D
B0,C0,D0=C
def at(txt,n=1):
    c=0
    for w in W:
        if w["text"].strip(".,:!?…—-").strip().lower()==txt.lower():
            c+=1
            if c==n: return w
    raise KeyError(txt)
vd=round(d["total"]-0.07,3)
PY=["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/headpos.py","b/person.webm"]
# big word behind him: «БАНКИ»
bw=at("банки"); a,b=round(bw["start"]-0.05,3),round(at("порядке")["start"],3)
head=json.loads(subprocess.check_output(PY+[json.dumps([round(a+0.3,2)])]).decode())[str(round(a+0.3,2))]["headTop"]
f={"family":"'Russo One', sans-serif","weight":400,"lineHeight":0.95}
lines=["БАНКИ"]; size=300
while max(ImageFont.truetype("/root/.fonts/RussoOne-Regular.ttf",size).getlength(l) for l in lines)>740: size-=5
big=[{"start":a,"end":b,"lines":lines,"size":size,"top":max(260,int(head+45-len(lines)*size*0.95)),"align":"center","font":f}]
# scene 3: main account goes down, backup keeps the business running
accounts={"start":B0,"end":C0,"cards":[{"title":"Банк №1","sub":"основной счёт","at":B0+0.05},{"title":"Банк №2","sub":"запасной счёт","at":at("операции")["start"]+0.35}],
  "badges":[{"at":at("операции")["start"],"card":0,"text":"Операции заблокированы","tone":"bad","anim":"flicker"},
            {"at":at("техработы")["start"],"card":0,"text":"Техработы","tone":"warn"},
            {"at":at("бизнес")["start"],"card":1,"text":"Бизнес работает","tone":"good","anim":"scale"}],
  "shield":{"at":at("страховка")["start"],"card":1,"text":"Страховка"}}
notes=[{"start":at("несколько")["start"],"end":D0,"text":"1 клиент → 4 заявки в разные банки","top":250}]
cta={"start":at("Ищи")["start"],"end":vd,"label":"Связки и порядок заявок — в бесплатном обучении","handle":"@jirafiktrafik"}
J="jirafik/"; S=[]
def add(t,src,vol): S.append({"at":round(t,3),"src":J+src,"volume":vol})
add(0.0,"sfx2-appear.wav",0.4)                                   # title
TR=[(B0,"zoomin"),(C0,"whip"),(D0,"whip")]
TS={"whip":("sfx2-swipe.wav",0.55,-0.12),"zoomin":("sfx2-zoom.wav",0.4,-0.2)}
for t_,ty in TR: src,vol,o=TS[ty]; add(t_+o,src,vol)
add(accounts["badges"][0]["at"],"sfx2-charge.wav",0.45)          # «заблокированы» flickers
add(accounts["shield"]["at"],"sfx2-appear.wav",0.4)              # shield appears
add(notes[0]["start"],"sfx2-whoosh-short.wav",0.4)               # pill scales in
add(cta["start"],"sfx2-whoosh-short.wav",0.4)                    # Telegram card
S.sort(key=lambda x:x["at"])
transitions=[{"at":t_,"type":ty,"dir":[1,-1][k%2]} for k,(t_,ty) in enumerate(TR)]
# angle: close-up after the jump cut in A, and once in D (not during the big word)
gaps=[(W[i]["end"],W[i+1]["start"]) for i in range(len(W)-1)]
dsw=round(at("рассказываю")["start"]-0.08,3)
asw=round(at("не")["start"]-0.06,3)
jr=[[asw,B0,0.18],[dsw,vd,0.18]]
mids=[round((r[0]+r[1])/2,2) for r in jr]
hp=json.loads(subprocess.check_output(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/headpos.py","b/person_full_probe.webm" if False else "b/person.webm",json.dumps(mids)]).decode())
for r,mm in zip(jr,mids):
    h=hp[str(mm)]
    r+=[44.0,40.0] if h["headTop"]>=1900 else [round(100*(h["headTop"]+170)/1920,1),round(100*h["cx"]/1080,1)]
props={"videoSrc":"jirafik/v6-cut.mp4","videoDuration":vd,"fps":60,"cuts":C,"whooshAt":[],"emphasis":[],
 "words":W,"stickers":[],"inserts":[],"cta":cta,"accounts":accounts,"notes":notes,
 "hook":{"tag":"","line1":"Не один счёт","line2":"а два-три","until":B0,"teaser":"зачем бизнесу запасной счёт","size":120,"line2At":at("два")["start"]-0.05},
 "hookStyle":"lower","captionStyle":"word","captionsFrom":B0,"sfx":S,
 "endCard":{"seconds":0,"question":"","handles":[]},
 "motion":{"push":0.015,"jumpZoom":0.12,"jumpRanges":jr,"alternate":False,"punch":0,"blur":0,"flash":False,"emphasisZoom":0.05,"vignette":False},
 "transitions":transitions,"plateTheme":"light","showProgress":False,"personSrc":"jirafik/v6-person.webm","bigWords":big}
json.dump(props,open("/home/user/OpenMontage/remotion-composer/public/demo-props/jirafik-acc6.json","w"),ensure_ascii=False,indent=1)
print("vd",vd,"jr",jr); print(big); print([(x["at"],x["src"].split('/')[-1]) for x in S])
