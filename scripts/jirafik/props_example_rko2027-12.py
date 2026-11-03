import json, subprocess, os
from PIL import ImageFont
d=json.load(open("timeline_n.json")); W=d["words"]
def at(txt,n=1):
    c=0
    for w in W:
        if w["text"].strip(".,:!?…—-«»").strip().lower()==txt.lower():
            c+=1
            if c==n: return w["start"]
    raise KeyError(txt)
vd=round(d["total"]-0.07,3)
# 5 parts after the hook; transitions between parts (none after the hook)
T1,T2,T3,T4=[round(x-0.15,3) for x in (at("За",3),at("И",2),at("Но"),at("Как",2))]
TRANS=[{"at":T1,"type":"whip","dir":1},{"at":T2,"type":"zoomin"},{"at":T3,"type":"dissolve"},{"at":T4,"type":"whip","dir":-1}]
notes=[{"start":at("Вообще"),"end":at("Банкам")-0.1,"text":"Направление работает уже около 6 лет","top":380},
       {"start":at("по-честному"),"end":at("Зато")-0.1,"text":"Не за один вечер: довести клиента и выполнить условия банков","top":380},
       {"start":at("Зато"),"end":T4-0.05,"text":"Без вложений · без опыта","top":380}]
boards=[{"start":at("Банкам")-0.05,"end":at("Соответственно")-0.1,"blocks":[
   {"at":at("Банкам"),"icon":"bank","title":"Банку нужны новые клиенты","sub":"без них банк не растёт"},
   {"at":at("Поэтому"),"icon":"coins","title":"Платит за каждого","sub":"приведённого клиента","tone":"good"}]},
  {"start":at("три")-0.05,"end":T3-0.05,"blocks":[
   {"at":at("где"),"icon":"people","title":"Искать клиентов"},
   {"at":at("общаться"),"icon":"doc","title":"Общаться"},
   {"at":at("продавать"),"icon":"coins","title":"Продавать","tone":"good"}]}]
chapters=[{"start":at("За",3),"end":T2-0.05,"kicker":"1","title":"клиент","value":"до 59 000 ₽","note":"клиент платит 0 ₽","noteAt":at("копейки")}]
a,b=round(at("Соответственно")-0.05,3),round(T1-0.05,3)
if not os.path.exists("b/person.webm"):
    subprocess.run(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/matte.py","b/cut_n.mp4","b/person.webm",str(a-0.5),str(b+0.5)],check=True)
head=json.loads(subprocess.check_output(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/headpos.py","b/person.webm",json.dumps([round(a+0.3,2)])]).decode())[str(round(a+0.3,2))]["headTop"]
f={"family":"'Russo One', sans-serif","weight":400,"lineHeight":0.95}
lines=["БАНКИ"]; size=400
while max(ImageFont.truetype("/root/.fonts/RussoOne-Regular.ttf",size).getlength(l) for l in lines)>900: size-=5
big=[{"start":a,"end":b,"lines":lines,"size":size,"top":max(340,int(head+60-size*0.95)),"align":"center","font":f}]
cta={"start":at("Как",2),"end":vd,"label":"Бесплатное обучение с нуля — в Telegram","handle":"@jirafiktrafik"}
J="jirafik/"; S=[]
def add(t,src,vol): S.append({"at":round(t,3),"src":J+src,"volume":vol})
add(0.0,"sfx2-appear.wav",0.4)
add(T1-0.12,"sfx2-swipe.wav",0.5)
add(T2-0.1,"sfx2-zoom.wav",0.4)
add(T3-0.05,"sfx2-appear.wav",0.3)
add(T4-0.12,"sfx2-swipe.wav",0.5)
S.sort(key=lambda x:x["at"])
Z=0.22
CLOSE=[(at("Банкам")-0.08,at("Соответственно")-0.05),(at("Причём")-0.08,T2-0.2),(at("где")-0.08,T3-0.2),
       (at("Зато")-0.08,T4-0.2),(at("Поэтому",2)-0.08,vd)]
jr=[[round(s0,3),round(e0,3),Z,50.0,50.0] for s0,e0 in CLOSE]
props={"videoSrc":"jirafik/v12n-cut.mp4","videoDuration":vd,"fps":60,"cuts":d["cuts"],"whooshAt":[],"emphasis":[],
 "words":W,"stickers":[],"inserts":[],"chapters":chapters,"notes":notes,"cta":cta,"boards":boards,
 "hook":{"tag":"","line1":"РКО в 2027","line2":"самая живая ниша","until":round(at("Смотри")-0.05,3),"teaser":"объясняю за минуту","size":124,"line2At":at("самая")-0.05},
 "hookStyle":"lower","captionStyle":"word","captionsFrom":round(at("Смотри")-0.05,3),"sfx":S,
 "endCard":{"seconds":0,"question":"","handles":[]},
 "motion":{"push":0.015,"jumpZoom":0.12,"jumpRanges":jr,"alternate":False,"punch":0,"blur":0,"flash":False,"emphasisZoom":0.05,"vignette":False},
 "transitions":TRANS,"plateTheme":"light","showProgress":False,"personSrc":"jirafik/v12-person.webm","bigWords":big}
P="/home/user/OpenMontage/remotion-composer/public/demo-props/"
json.dump(props,open(P+"jirafik-rko2027-12.json","w"),ensure_ascii=False,indent=1)
json.dump(dict(props,overlayOnly=True,transitions=[]),open(P+"jirafik-rko2027-12-ovl.json","w"),ensure_ascii=False,indent=1)
print("T",T1,T2,T3,T4); print(big); print(jr); print([(x["at"],x["src"].split('/')[-1]) for x in S])
