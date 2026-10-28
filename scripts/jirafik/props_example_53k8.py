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
# take changes (re-recorded parts, found by scene detection on the cut)
T1,T2,T3,T4=9.933,14.85,50.717,63.683
# face centre x per take (share of width) - he sits a bit left of centre
TAKES=[(0,T1,0.44),(T1,T2,0.43),(T2,T3,0.46),(T3,T4,0.39),(T4,vd,0.39)]
def xh(t): return next(x for a,b,x in TAKES if a<=t<b)
chapters=[
 {"start":T1+0.05,"end":T2-0.05,"kicker":"№1","title":"Альфа-Банк","value":"14 000 ₽","note":"просто за открытие счёта","noteAt":at("просто")},
 {"start":T2+0.05,"end":at("Следующий")-0.08,"kicker":"№2","title":"Т-Банк","value":"10 000 – 20 000 ₽","note":"зависит от формата регистрации","noteAt":at("оплата")},
 {"start":at("Следующий"),"end":at("Четвёртый")-0.08,"kicker":"№3","title":"Ozon Банк","value":"8 000 ₽","note":"клиент должен быть активен","noteAt":at("должен")},
 {"start":at("Четвёртый"),"end":at("Далее")-0.08,"kicker":"№4","title":"ВТБ","value":"8 000 ₽","note":"пополнить счёт на 5 000 ₽ и подержать сутки","noteAt":at("пополнить")},
 {"start":at("Далее"),"end":T3-0.05,"kicker":"№5","title":"ПСБ","value":"9 000 ₽","note":"платный тариф (690 ₽), бизнесу от 4 месяцев","noteAt":at("платном")},
 {"start":T3+0.05,"end":at("3 000 ₽")+0.8,"kicker":"№6","title":"Сбер","value":"4 000 ₽","note":"+3 000 ₽ приглашённому клиенту","noteAt":at("приглашённый")}]
calc={"start":at("3 000 ₽")+0.85,"end":at("связки")-0.1,"parts":["14 000","10 000","8 000","8 000","9 000","4 000"],"total":"53 000 ₽"}
# big word behind him
a,b=round(at("связки")-0.05,3),round(at("НПД")+0.6,3)
subprocess.run(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/matte.py","b/cut.mp4","b/person.webm",str(a-0.5),str(b+0.5)],check=True)
head=json.loads(subprocess.check_output(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/headpos.py","b/person.webm",json.dumps([round(a+0.3,2)])]).decode())[str(round(a+0.3,2))]["headTop"]
f={"family":"'Russo One', sans-serif","weight":400,"lineHeight":0.95}
lines=["ИП НА","НПД"]; size=300
while max(ImageFont.truetype("/root/.fonts/RussoOne-Regular.ttf",size).getlength(l) for l in lines)>900: size-=5
big=[{"start":a,"end":b,"lines":lines,"size":size,"top":max(340,int(head+45-len(lines)*size*0.95)),"align":"center","font":f}]
cta={"start":at("А"),"end":vd,"label":"Порядок открутки — в бесплатном обучении","handle":"@jirafiktrafik"}
J="jirafik/"; S=[]
def add(t,src,vol): S.append({"at":round(t,3),"src":J+src,"volume":vol})
add(0.0,"sfx2-appear.wav",0.4)
TR=[(T1,"whip"),(T2,"whip"),(T3,"whip"),(T4,"whip")]
for t_,ty in TR: add(t_-0.12,"sfx2-swipe.wav",0.55)
# chips that don't arrive together with a whip get their own short whoosh
for c in chapters:
    if all(abs(c["start"]-t_)>0.3 for t_,_ in TR): add(c["start"],"sfx2-whoosh-short.wav",0.35)
add(calc["start"],"sfx2-gauge.wav",0.35)
add(big[0]["start"],"sfx2-zoom.wav",0.35)
S.sort(key=lambda x:x["at"])
transitions=[{"at":t_,"type":ty,"dir":[1,-1][k%2]} for k,(t_,ty) in enumerate(TR)]
# angle changes every ~4-6 s: close-ups zoom around the frame centre (head stays below the chips) and
# shift sideways so he ends up centred
Z=0.22
CLOSE=[(at("При")-0.08,T1),(at("Но")-0.08,at("Следующий")-0.05),(at("Но",2)-0.08,at("Четвёртый")-0.05),
       (at("Здесь")-0.08,at("И")-0.05),(at("можно")-0.08,T3),(at("Но",4)-0.08,calc["start"]),(T4,vd)]
jr=[]
for s0,e0 in CLOSE:
    x=xh(s0+0.01); ox=max(0.0,min(1.0,((1+Z)*x-0.5)/Z))
    jr.append([round(s0,3),round(e0,3),Z,50.0,round(100*ox,1)])
props={"videoSrc":"jirafik/v8-cut.mp4","videoDuration":vd,"fps":60,"cuts":d["cuts"],"whooshAt":[],"emphasis":[],
 "words":W,"stickers":[],"inserts":[],"chapters":chapters,"calc":calc,"cta":cta,
 "hook":{"tag":"","line1":"53 000 ₽","line2":"за одного клиента","until":round(at("При")-0.05,3),"teaser":"а клиент не отдал ни копейки","size":124,"line2At":at("за")-0.05},
 "hookStyle":"lower","captionStyle":"word","captionsFrom":round(at("При")-0.05,3),"sfx":S,
 "endCard":{"seconds":0,"question":"","handles":[]},
 "motion":{"push":0.015,"jumpZoom":0.12,"jumpRanges":jr,"alternate":False,"punch":0,"blur":0,"flash":False,"emphasisZoom":0.05,"vignette":False},
 "transitions":transitions,"plateTheme":"light","showProgress":False,"personSrc":"jirafik/v8-person.webm","bigWords":big}
json.dump(props,open("/home/user/OpenMontage/remotion-composer/public/demo-props/jirafik-53k8.json","w"),ensure_ascii=False,indent=1)
print("vd",vd); print(big); print(jr); print([(x["at"],x["src"].split('/')[-1]) for x in S])
