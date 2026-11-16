import json, subprocess, os
from PIL import ImageFont
d=json.load(open("timeline_n.json")); W=d["words"]
exec(open("build.py").read().split("words=[]")[0])   # pieces + mp() from the same cut list
def iw(i): return round(mp(g[i]["start"]),3)
vd=round(d["total"]-0.07,3)
# the list builds up as each offer is named; total = the 71 000 ₽ he states
rows=[("Озон Банк","5 000 ₽",36),("РСХБ","7 000 ₽",49),("ВТБ","8 000 ₽",69),("Т-Банк","10 000 ₽",85),
      ("Сбербанк","10 000 ₽",120),("ПСБ","11 000 ₽",136),("Альфа-Банк","14 000 ₽",151),("Симка Билайн","6 000 ₽",179)]
table={"start":iw(33)-0.05,"end":iw(185)-0.1,"title":"8 офферов: выплата за 1 клиента",
  "rows":[{"at":iw(i),"name":n,"value":v} for n,v,i in rows],
  "totalAt":iw(179)+0.3,"total":71000,"columns":2,"width":860,"shiftX":-50}
notes=[{"start":iw(20)-0.05,"end":iw(33)-0.1,"text":"Бесплатный гайд по всем 8 офферам — в конце","top":380},
       {"start":iw(193),"end":iw(198)-0.1,"text":"Что такое РКО — видео закреплено в профиле","top":380}]
a,b=round(iw(185)-0.05,3),round(iw(193)-0.1,3)
if not os.path.exists("b/person.webm"): subprocess.run(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/matte.py","b/cut_n.mp4","b/person.webm",str(a-0.5),str(b+0.5)],check=True)
f={"family":"'Russo One', sans-serif","weight":400,"lineHeight":0.95}
lines=["РКО"]; size=420
while max(ImageFont.truetype("/root/.fonts/RussoOne-Regular.ttf",size).getlength(l) for l in lines)>740: size-=5
big=[{"start":a,"end":b,"lines":lines,"size":size,"top":700,"align":"center","font":f}]
cta={"start":iw(198),"end":vd,"label":"Бесплатное обучение — в Telegram","handle":"@jirafiktrafik"}
Z=0.22
CLOSE=[(iw(12)-0.08,iw(20)-0.05),(iw(82)-0.08,iw(116)-0.05),(iw(148)-0.08,iw(164)-0.05),(iw(198)-0.08,vd)]
jr=[[round(s0,3),round(e0,3),Z,50.0,50.0] for s0,e0 in CLOSE]
props={"videoSrc":"jirafik/v17n-cut.mp4","videoDuration":vd,"fps":60,"cuts":d["cuts"],"whooshAt":[],"emphasis":[],
 "words":W,"stickers":[],"inserts":[],"chapters":[],"notes":notes,"cta":cta,"boards":[],"table":table,
 "hook":{"tag":"","line1":"8 банков","line2":"= 71 000 ₽","until":round(iw(20)-0.05,3),"teaser":"за одного клиента","size":120,"line2At":iw(8)-0.05},
 "hookStyle":"lower","captionStyle":"word","captionsFrom":round(iw(20)-0.05,3),"sfx":[],
 "endCard":{"seconds":0,"question":"","handles":[]},
 "motion":{"push":0.015,"jumpZoom":0.12,"jumpRanges":jr,"alternate":False,"punch":0,"blur":0,"flash":False,"emphasisZoom":0.05,"vignette":False},
 "transitions":[],"plateTheme":"light","showProgress":False,"personSrc":"jirafik/v17-person.webm","bigWords":big}
P="/home/user/OpenMontage/remotion-composer/public/demo-props/"
json.dump(props,open(P+"jirafik-8bankov17.json","w"),ensure_ascii=False,indent=1)
json.dump(dict(props,overlayOnly=True),open(P+"jirafik-8bankov17-ovl.json","w"),ensure_ascii=False,indent=1)
print("vd",vd); print(jr); print(table["rows"],table["totalAt"])
