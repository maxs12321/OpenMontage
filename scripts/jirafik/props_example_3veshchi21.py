import json, subprocess, os
from PIL import ImageFont
d=json.load(open("timeline_n.json")); W=d["words"]
exec(open("build.py").read().split("words=[]")[0])   # pieces + mp() from the same cut list
def iw(i): return round(mp(g[i]["start"]),3)
vd=round(d["total"]-0.07,3)
notes=[{"start":iw(21)-0.05,"end":iw(29)-0.1,"text":"Бесплатный гайд по нише — в конце","top":380},
       {"start":iw(136),"end":iw(148)-0.1,"text":"Что такое РКО — видео закреплено в профиле","top":380}]
boards=[{"start":iw(29)-0.05,"end":iw(47)-0.1,"blocks":[
   {"at":iw(29),"icon":"doc","title":"1. Техническая часть","sub":"партнёрские сети"},
   {"at":iw(42),"icon":"coins","title":"14 000 ₽ вместо 3 000 ₽","sub":"за расчётный счёт через партнёрскую сеть","tone":"good"}]},
  {"start":iw(47)-0.05,"end":iw(68)-0.1,"blocks":[
   {"at":iw(47),"icon":"bank","title":"Читай условия банков","sub":"без этого не получишь оплату",
    "chips":[{"at":iw(66),"text":"целевое действие","tone":"warn"}]}]},
  {"start":iw(68)-0.05,"end":iw(105)-0.1,"blocks":[
   {"at":iw(68),"icon":"people","title":"2. Связки","sub":"где искать людей, которым реально нужен счёт"},
   {"at":iw(87),"icon":"coins","title":"Стабильность","sub":"одна связка — люди каждый месяц","tone":"good"}]},
  {"start":iw(105)-0.05,"end":iw(128)-0.1,"blocks":[
   {"at":iw(105),"icon":"bank","title":"3. Банки платят не всегда","sub":"где-то откажут, где-то не выполнено условие","tone":"bad"},
   {"at":iw(123),"icon":"doc","title":"Это нормально","sub":"так устроена ниша","tone":"good"}]}]
a,b=round(iw(128)-0.05,3),round(iw(136)-0.1,3)
if not os.path.exists("b/person.webm"): subprocess.run(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/matte.py","b/cut_n.mp4","b/person.webm",str(a-0.5),str(b+0.5)],check=True)
f={"family":"'Russo One', sans-serif","weight":400,"lineHeight":0.95}
lines=["3 ВЕЩИ"]; size=420
while max(ImageFont.truetype("/root/.fonts/RussoOne-Regular.ttf",size).getlength(l) for l in lines)>740: size-=5
big=[{"start":a,"end":b,"lines":lines,"size":size,"top":700,"align":"center","font":f}]
cta={"start":iw(148),"end":vd,"label":"Бесплатное обучение — в Telegram","handle":"@jirafiktrafik"}
Z=0.22
CLOSE=[(iw(47)-0.08,iw(68)-0.05),(iw(105)-0.08,iw(128)-0.05),(iw(148)-0.08,vd)]
jr=[[round(s0,3),round(e0,3),Z,50.0,50.0] for s0,e0 in CLOSE]
props={"videoSrc":"jirafik/v21n-cut.mp4","videoDuration":vd,"fps":60,"cuts":d["cuts"],"whooshAt":[],"emphasis":[],
 "words":W,"stickers":[],"inserts":[],"chapters":[],"notes":notes,"cta":cta,"boards":boards,
 "hook":{"tag":"","line1":"Стабильный доход","line2":"3 вещи, без которых никак","until":round(iw(13)-0.05,3),"teaser":"РКО","size":110,"line2At":iw(7)-0.05},
 "hookStyle":"lower","captionStyle":"word","captionsFrom":round(iw(13)-0.05,3),"sfx":[],
 "endCard":{"seconds":0,"question":"","handles":[]},
 "motion":{"push":0.015,"jumpZoom":0.12,"jumpRanges":jr,"alternate":False,"punch":0,"blur":0,"flash":False,"emphasisZoom":0.05,"vignette":False},
 "transitions":[],"plateTheme":"light","showProgress":False,"personSrc":"jirafik/v21-person.webm","bigWords":big}
P="/home/user/OpenMontage/remotion-composer/public/demo-props/"
json.dump(props,open(P+"jirafik-3veshchi21.json","w"),ensure_ascii=False,indent=1)
json.dump(dict(props,overlayOnly=True),open(P+"jirafik-3veshchi21-ovl.json","w"),ensure_ascii=False,indent=1)
print("vd",vd); print(jr)
