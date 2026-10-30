import json, subprocess
from PIL import ImageFont
d=json.load(open("timeline.json")); W=d["words"]
def at(txt,n=1):
    c=0
    for w in W:
        if w["text"].strip(".,:!?…—-").strip().lower()==txt.lower():
            c+=1
            if c==n: return w["start"]
    raise KeyError(txt)
vd=round(d["total"]-0.07,3)
chapters=[
 {"start":at("Один"),"end":at("Если")-0.1,"kicker":"1","title":"клиент","value":"≈ 53 000 ₽","note":"платят банки, не клиент","noteAt":at("Платят")},
 {"start":at("Человек",2),"end":at("Если",2)-0.1,"kicker":"ИП","title":"на НПД","value":"→ счета в банках","note":"банк платит за приведённого клиента","noteAt":at("а")},
 {"start":at("Найти"),"end":at("Найти",2)-0.08,"kicker":"3","title":"человека за месяц","value":"реально"},
 {"start":at("Найти",2),"end":at("Ну")-0.1,"kicker":"30","title":"человек","value":"гораздо тяжелее"}]
calc={"start":at("математика"),"end":at("Найти")-0.15,"parts":["53 000","53 000","53 000"],"total":"159 000 ₽"}
notes=[{"start":at("Если",2),"end":at("Теперь")-0.15,"text":"Что такое РКО — видео закреплено в профиле","top":380},
       {"start":at("по-честному"),"end":at("Но",2)-0.1,"text":"Не за один вечер: довести клиента и выполнить условия банков","top":380},
       {"start":at("порог"),"end":at("Как")-0.1,"text":"Без вложений · без офиса · без опыта","top":380}]
# big word behind him
a,b=round(at("РКО")-0.05,3),round(at("счета")-0.05,3)
subprocess.run(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/matte.py","b/cut_c.mp4","b/person.webm",str(a-0.5),str(b+0.5)],check=True)
head=json.loads(subprocess.check_output(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/headpos.py","b/person.webm",json.dumps([round(a+0.3,2)])]).decode())[str(round(a+0.3,2))]["headTop"]
f={"family":"'Russo One', sans-serif","weight":400,"lineHeight":0.95}
lines=["РКО"]; size=420
while max(ImageFont.truetype("/root/.fonts/RussoOne-Regular.ttf",size).getlength(l) for l in lines)>900: size-=5
big=[{"start":a,"end":b,"lines":lines,"size":size,"top":max(340,int(head+60-size*0.95)),"align":"center","font":f}]
cta={"start":at("Как"),"end":vd,"label":"Как получать 53 000 ₽ с клиента — в бесплатном обучении","handle":"@jirafiktrafik"}
J="jirafik/"; S=[]
def add(t,src,vol): S.append({"at":round(t,3),"src":J+src,"volume":vol})
add(0.0,"sfx2-appear.wav",0.4)
for c in chapters: add(c["start"],"sfx2-whoosh-short.wav",0.35)
add(big[0]["start"],"sfx2-zoom.wav",0.35)
add(calc["start"]+0.6,"sfx2-gauge.wav",0.35)
add(cta["start"],"sfx2-whoosh-short.wav",0.4)
S.sort(key=lambda x:x["at"])
# angle every ~5 s: straight centred close-ups (no sideways shift)
Z=0.22
CLOSE=[(at("И")-0.08,at("Нужно",2)-0.05),(at("Сейчас")-0.08,at("Один")-0.05),(at("Платят")-0.08,at("Если")-0.05),
       (at("к")-0.08,at("Если",2)-0.05),(at("там")-0.08,at("Теперь")-0.05),(at("Найти")-0.08,at("Найти",2)-0.05),
       (at("по-честному")-0.08,at("Но",2)-0.05),(at("Как")-0.08,vd)]
jr=[[round(s0,3),round(e0,3),Z,50.0,50.0] for s0,e0 in CLOSE]
props={"videoSrc":"jirafik/v10-cut.mp4","videoDuration":vd,"fps":60,"cuts":d["cuts"],"whooshAt":[],"emphasis":[],
 "words":W,"stickers":[],"inserts":[],"chapters":chapters,"calc":calc,"notes":notes,"cta":cta,
 "hook":{"tag":"","line1":"150 000 ₽","line2":"за первый месяц","until":round(at("Сейчас")-0.05,3),"teaser":"нужно всего 3 человека","size":124,"line2At":at("за")-0.05},
 "hookStyle":"lower","captionStyle":"word","captionsFrom":round(at("Сейчас")-0.05,3),"sfx":S,
 "endCard":{"seconds":0,"question":"","handles":[]},
 "motion":{"push":0.015,"jumpZoom":0.12,"jumpRanges":jr,"alternate":False,"punch":0,"blur":0,"flash":False,"emphasisZoom":0.05,"vignette":False},
 "transitions":[],"plateTheme":"light","showProgress":False,"personSrc":"jirafik/v10-person.webm","bigWords":big}
json.dump(props,open("/home/user/OpenMontage/remotion-composer/public/demo-props/jirafik-150k10.json","w"),ensure_ascii=False,indent=1)
print("vd",vd); print(big); print(jr); print([(x["at"],x["src"].split('/')[-1]) for x in S])
