import json, subprocess
from PIL import ImageFont
d=json.load(open("timeline.json")); W=d["words"]; SH=d["shots"]
def at(txt,n=1):
    c=0
    for w in W:
        if w["text"].strip(".,:!?…—-").strip().lower()==txt.lower():
            c+=1
            if c==n: return w["start"]
    raise KeyError(txt)
vd=round(d["total"]-0.07,3)
B=[s[0] for s in SH[1:]]            # shot changes: F1|D1, D1|F2, F2|D2, D2|F3, F3|D3, D3|F4
D1,F2,D2,F3,D3,F4=B
# big word behind him
a,b=round(at("комиссию")-0.05,3),round(at("Клиенту")+0.05,3)
head=json.loads(subprocess.check_output(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/headpos.py","b/person.webm",json.dumps([round(a+0.3,2)])]).decode())[str(round(a+0.3,2))]["headTop"]
f={"family":"'Russo One', sans-serif","weight":400,"lineHeight":0.95}
lines=["КОМИССИЯ"]; size=300
while max(ImageFont.truetype("/root/.fonts/RussoOne-Regular.ttf",size).getlength(l) for l in lines)>740: size-=5
big=[{"start":a,"end":b,"lines":lines,"size":size,"top":max(340,int(head+45-len(lines)*size*0.95)),"align":"center","font":f}]
tstart=round(at("таблица")-0.1,3); tend=round(at("открутка")+0.75,3)
table={"start":tstart,"end":tend,"title":"Офферы за одного клиента","rows":[
  {"at":at("Альфа-Банк"),"name":"Альфа-Банк","value":"14 000 ₽"},
  {"at":at("ВТБ"),"name":"ВТБ","value":"8 000 ₽"},
  {"at":at("Т-Банк"),"name":"Т-Банк","value":"10 000 ₽"},
  {"at":at("ПСБ"),"name":"ПСБ","value":"9 000 ₽"},
  {"at":at("Сбербанк"),"name":"Сбербанк","value":"4 000 ₽","note":"+3 000 ₽ клиенту"},
  {"at":at("Озон"),"name":"Ozon Банк","value":"8 000 ₽"},
  {"at":at("корпоративная"),"name":"Симка Билайн","value":"6 000 ₽","note":"бонус"}],
  "totalAt":at("выходит"),"total":59000,"stamp":{"at":at("закрытая"),"text":"Закрытая открутка ✓"},"columns":2,"blur":False}
boards=[
 {"start":D1,"end":F2,"blocks":[
   {"at":D1+0.15,"icon":"doc","title":"РКО","sub":"расчётно-кассовое обслуживание","chips":[{"at":at("счёт"),"text":"счёт для бизнеса"}]},
   {"at":at("Банкам"),"icon":"bank","title":"Банк платит","sub":"за каждого привлечённого клиента"},
   {"at":at("Вместо"),"icon":"tv","title":"Реклама по ТВ","sub":"рекламный бюджет банка","crossAt":at("телевизору")},
   {"at":at("банк"),"icon":"coins","title":"Тому, кто привёл клиента","tone":"good"}]},
 {"start":D2,"end":F3,"blocks":[
   {"at":D2+0.15,"icon":"doc","title":"ИП на НПД","sub":"упрощённый режим","chips":[{"at":at("без"),"text":"без страховых взносов"},{"at":at("отчётности"),"text":"без отчётности"}]},
   {"at":at("Дальше"),"icon":"card","title":"Не один счёт, а несколько","sub":"в разных банках","tone":"good"},
   {"at":at("Предприниматели"),"icon":"bank","title":"Деньги не держат в одном банке","chips":[{"at":at("блокировки"),"text":"блокировки","tone":"bad"},{"at":at("технические"),"text":"техработы","tone":"warn"},{"at":at("заморозка"),"text":"заморозка операций","tone":"bad"}]}]},
 {"start":tend-0.05,"end":F4,"blocks":[
   {"at":tend,"icon":"people","title":"Толпа клиентов","sub":"не нужна","crossAt":at("клиентов")+0.3},
   {"at":at("большие"),"icon":"coins","title":"Большие ставки","sub":"за банковские продукты","tone":"good"},
   {"at":at("открывают"),"icon":"card","title":"Пара счетов по 3 000 ₽","tone":"bad","chips":[{"at":at("окупается"),"text":"«ниша не окупается»","tone":"bad"}]}]}]
cta={"start":at("Ищи"),"end":vd,"label":"Где взять офферы — в бесплатном обучении","handle":"@jirafiktrafik"}
J="jirafik/"; S=[]
def add(t,src,vol): S.append({"at":round(t,3),"src":J+src,"volume":vol})
add(0.0,"sfx2-appear.wav",0.4)
TR=[(D1,"zoomin"),(F2,"whip"),(D2,"whip"),(F3,"whip"),(D3,"dissolve"),(F4,"whip")]
TS={"whip":("sfx2-swipe.wav",0.55,-0.12),"zoomin":("sfx2-zoom.wav",0.4,-0.2),"dissolve":("sfx2-whoosh-short.wav",0.3,-0.05)}
for t_,ty in TR: src,vol,o=TS[ty]; add(t_+o,src,vol)
add(big[0]["start"],"sfx2-zoom.wav",0.35)
add(table["totalAt"],"sfx2-gauge.wav",0.35)
add(table["stamp"]["at"],"sfx2-whoosh-short.wav",0.4)
add(cta["start"],"sfx2-whoosh-short.wav",0.4)
S.sort(key=lambda x:x["at"])
transitions=[{"at":t_,"type":ty,"dir":[1,-1][k%2]} for k,(t_,ty) in enumerate(TR)]
# close-up: anchor the zoom at the bottom edge so the wall above is cropped and his face rises,
# and shift sideways so he ends up centred (he sits left of centre: face ~ x 0.43, y 0.55)
Z=0.15; XH=0.43
ox=max(0.0,min(1.0,((1+Z)*XH-0.5)/Z))
jr=[[round(at("При")-0.08,3),D1,Z],[round(at("Клиенту")-0.06,3),D2,Z],[round(at("Где")-0.1,3),vd,Z]]
for r in jr: r+=[100.0,round(100*ox,1)]
props={"videoSrc":"jirafik/v7-cut.mp4","videoDuration":vd,"fps":60,"cuts":d["cuts"],"whooshAt":[],"emphasis":[],
 "words":W,"stickers":[],"inserts":[],"cta":cta,"boards":boards,"table":table,
 "hook":{"tag":"","line1":"59 000 ₽","line2":"за одного клиента","until":round(at("При")-0.05,3),"teaser":"а клиент не платит ни копейки","size":124,"line2At":at("за")-0.05},
 "hookStyle":"lower","captionStyle":"word","captionsFrom":round(at("При")-0.05,3),"sfx":S,
 "endCard":{"seconds":0,"question":"","handles":[]},
 "motion":{"push":0.015,"jumpZoom":0.12,"jumpRanges":jr,"alternate":False,"punch":0,"blur":0,"flash":False,"emphasisZoom":0.05,"vignette":False},
 "transitions":transitions,"plateTheme":"light","showProgress":False,"personSrc":"jirafik/v7-person.webm","bigWords":big}
json.dump(props,open("/home/user/OpenMontage/remotion-composer/public/demo-props/jirafik-59k7.json","w"),ensure_ascii=False,indent=1)
print("vd",vd,"shots",B); print(big); print([(x["at"],x["src"].split('/')[-1]) for x in S])
