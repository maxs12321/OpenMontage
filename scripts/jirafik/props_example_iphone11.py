import json, subprocess
from PIL import ImageFont
d=json.load(open("timeline_n.json")); W=d["words"]
def at(txt,n=1):
    c=0
    for w in W:
        if w["text"].strip(".,:!?…—-").strip().lower()==txt.lower():
            c+=1
            if c==n: return w["start"]
    raise KeyError(txt)
vd=round(d["total"]-0.07,3)
# courier vs me
boards=[{"start":at("Для")-0.05,"end":at("За")-0.1,"blocks":[
  {"at":at("Для"),"icon":"people","title":"Курьер","sub":"полтора месяца на ногах","tone":"bad","crossAt":at("а")},
  {"at":at("а"),"icon":"coins","title":"Я","sub":"2 разговора","tone":"good"}]}]
chapters=[{"start":at("За"),"end":at("Нахожу")-0.08,"kicker":"1","title":"клиент","value":"53 000 ₽","note":"платят банки","noteAt":at("банки")}]
calc={"start":at("Нахожу"),"end":at("Вот")-0.12,"parts":["53 000","53 000"],"total":"106 000 ₽"}
rows=[("Альфа-Банк","14 000 ₽","за открытие счёта"),("Т-Банк","10–20 тыс. ₽","зависит от формата регистрации"),
      ("Ozon Банк","8 000 ₽","клиент должен быть активен"),("ВТБ","8 000 ₽","пополнить на 5 000 ₽ и подержать сутки"),
      ("ПСБ","9 000 ₽","платный тариф 690 ₽, бизнесу от 4 мес."),("Сбер","4 000 ₽","+3 000 ₽ приглашённому клиенту")]
t0=at("банков")
table={"start":at("Вот")-0.05,"end":at("Сейчас")-0.1,"title":"Мои банки: выплата за 1 клиента",
  "rows":[{"at":round(t0+0.3*i,3),"name":n,"value":v} for i,(n,v,no) in enumerate(rows)],
  "totalAt":round(t0+1.9,3),"total":53000,"columns":2}
accounts={"start":at("Открывает")-0.05,"end":at("Более")-0.1,
  "cards":[{"title":"Банк 1","sub":"бизнес-счёт","at":at("бизнес-счета")},{"title":"Банк 2","sub":"запасной счёт","at":at("несколько")}],
  "badges":[{"at":at("технические"),"card":0,"text":"техработы","tone":"bad","anim":"flicker"},
            {"at":at("встанет"),"card":1,"text":"бизнес работает","tone":"good","anim":"scale"}]}
notes=[{"start":at("яйца")-0.3,"end":at("Например")-0.1,"text":"Не хранить все яйца в одной корзине","top":1330},
       {"start":at("рассказываю"),"end":at("А",2)-0.1,"text":"Что такое РКО — видео закреплены в профиле","top":380}]
a,b=round(at("РКО")-0.05,3),round(at("рассказываю")-0.1,3)
import os
if not os.path.exists("b/person.webm"): subprocess.run(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/matte.py","b/cut_n.mp4","b/person.webm",str(a-0.5),str(b+0.5)],check=True)
head=json.loads(subprocess.check_output(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/headpos.py","b/person.webm",json.dumps([round(a+0.3,2)])]).decode())[str(round(a+0.3,2))]["headTop"]
f={"family":"'Russo One', sans-serif","weight":400,"lineHeight":0.95}
lines=["РКО"]; size=420
while max(ImageFont.truetype("/root/.fonts/RussoOne-Regular.ttf",size).getlength(l) for l in lines)>900: size-=5
big=[{"start":a,"end":b,"lines":lines,"size":size,"top":max(340,int(head+60-size*0.95)),"align":"center","font":f}]
cta={"start":at("А",2),"end":vd,"label":"Бесплатное обучение с нуля — в Telegram","handle":"@jirafiktrafik"}
J="jirafik/"; S=[]
def add(t,src,vol): S.append({"at":round(t,3),"src":J+src,"volume":vol})
add(0.0,"sfx2-appear.wav",0.4)
add(boards[0]["start"],"sfx2-whoosh-short.wav",0.35)
add(chapters[0]["start"],"sfx2-whoosh-short.wav",0.35)
add(calc["start"]+0.6,"sfx2-gauge.wav",0.35)
add(table["start"],"sfx2-swipe.wav",0.4)
add(accounts["start"],"sfx2-whoosh-short.wav",0.35)
add(big[0]["start"],"sfx2-zoom.wav",0.35)
add(cta["start"],"sfx2-whoosh-short.wav",0.4)
S.sort(key=lambda x:x["at"])
Z=0.22
CLOSE=[(at("Для")-0.08,at("За")-0.05),(at("Нахожу")-0.08,at("Вот")-0.05),(at("Что")-0.08,at("Открывает")-0.05),
       (at("Например")-0.08,at("Более")-0.05),(at("А",2)-0.08,vd)]
jr=[[round(s0,3),round(e0,3),Z,50.0,50.0] for s0,e0 in CLOSE]
props={"videoSrc":"jirafik/v11n-cut.mp4","videoDuration":vd,"fps":60,"cuts":d["cuts"],"whooshAt":[],"emphasis":[],
 "words":W,"stickers":[],"inserts":[],"chapters":chapters,"calc":calc,"notes":notes,"cta":cta,"boards":boards,"table":table,"accounts":accounts,
 "hook":{"tag":"","line1":"iPhone 18 Pro","line2":"= 2 человека","until":round(at("Для")-0.05,3),"teaser":"а не 2 месяца на смене","size":124,"line2At":at("2")-0.05},
 "hookStyle":"lower","captionStyle":"word","captionsFrom":round(at("Для")-0.05,3),"sfx":S,
 "endCard":{"seconds":0,"question":"","handles":[]},
 "motion":{"push":0.015,"jumpZoom":0.12,"jumpRanges":jr,"alternate":False,"punch":0,"blur":0,"flash":False,"emphasisZoom":0.05,"vignette":False},
 "transitions":[],"plateTheme":"light","showProgress":False,"personSrc":"jirafik/v11-person.webm","bigWords":big}
P="/home/user/OpenMontage/remotion-composer/public/demo-props/"
json.dump(props,open(P+"jirafik-iphone11.json","w"),ensure_ascii=False,indent=1)
json.dump(dict(props,overlayOnly=True),open(P+"jirafik-iphone11-ovl.json","w"),ensure_ascii=False,indent=1)
print("vd",vd); print(big); print(jr); print([(x["at"],x["src"].split('/')[-1]) for x in S])
