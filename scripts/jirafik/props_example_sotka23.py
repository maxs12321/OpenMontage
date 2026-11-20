import json, subprocess, os
from PIL import ImageFont
d=json.load(open("timeline_n.json")); W=d["words"]
exec(open("build.py").read().split("words=[]")[0])   # pieces + mp() from the same cut list
def iw(i): return round(mp(g[i]["start"]),3)
vd=round(d["total"]-0.07,3)
notes=[{"start":iw(13)-0.05,"end":iw(26)-0.1,"text":"Бесплатный гайд по нише — в конце","top":380},
       {"start":iw(138),"end":iw(150)-0.1,"text":"Что такое РКО — видео закреплено в профиле","top":380}]
boards=[{"start":iw(26)-0.05,"end":iw(47)-0.1,"blocks":[
   {"at":iw(26),"icon":"bank","title":"8 офферов","sub":"все банки на одного человека"},
   {"at":iw(39),"icon":"coins","title":"71 000 ₽","sub":"в сумме за одного клиента","tone":"good"}]},
  {"start":iw(47)-0.05,"end":iw(72)-0.1,"blocks":[
   {"at":iw(47),"icon":"bank","title":"Так бывает не всегда","sub":"где-то банк откажет, где-то не пройдёт условия","tone":"bad"}]},
  {"start":iw(72)-0.05,"end":iw(107)-0.1,"blocks":[
   {"at":iw(72),"icon":"doc","title":"71 000 ₽ ÷ 8 ≈ 9 000 ₽","sub":"в среднем за один оффер"},
   {"at":iw(89),"icon":"coins","title":"Половина = 35 000 ₽","sub":"4 оффера с одного человека","tone":"good"}]},
  {"start":iw(107)-0.05,"end":iw(127)-0.1,"blocks":[
   {"at":iw(107),"icon":"people","title":"3 человека = первая сотка","sub":"найти 3 человека за месяц — реально","tone":"good"}]}]
a,b=round(iw(127)-0.05,3),round(iw(138)-0.1,3)
if not os.path.exists("b/person.webm"): subprocess.run(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/matte.py","b/cut_n.mp4","b/person.webm",str(a-0.5),str(b+0.5)],check=True)
f={"family":"'Russo One', sans-serif","weight":400,"lineHeight":0.95}
lines=["БАНКИ"]; size=420
while max(ImageFont.truetype("/root/.fonts/RussoOne-Regular.ttf",size).getlength(l) for l in lines)>740: size-=5
big=[{"start":a,"end":b,"lines":lines,"size":size,"top":700,"align":"center","font":f}]
cta={"start":iw(150),"end":vd,"label":"Бесплатное обучение — в Telegram","handle":"@jirafiktrafik"}
Z=0.22
CLOSE=[(iw(47)-0.08,iw(72)-0.05),(iw(107)-0.08,iw(127)-0.05),(iw(150)-0.08,vd)]
jr=[[round(s0,3),round(e0,3),Z,50.0,50.0] for s0,e0 in CLOSE]
props={"videoSrc":"jirafik/v23n-cut.mp4","videoDuration":vd,"fps":60,"cuts":d["cuts"],"whooshAt":[],"emphasis":[],
 "words":W,"stickers":[],"inserts":[],"chapters":[],"notes":notes,"cta":cta,"boards":boards,
 "hook":{"tag":"","line1":"100 000 ₽","line2":"первые деньги в РКО","until":round(iw(13)-0.05,3),"teaser":"РКО","size":110,"line2At":iw(8)-0.05},
 "hookStyle":"lower","captionStyle":"word","captionsFrom":round(iw(13)-0.05,3),"sfx":[],
 "endCard":{"seconds":0,"question":"","handles":[]},
 "motion":{"push":0.015,"jumpZoom":0.12,"jumpRanges":jr,"alternate":False,"punch":0,"blur":0,"flash":False,"emphasisZoom":0.05,"vignette":False},
 "transitions":[],"plateTheme":"light","showProgress":False,"personSrc":"jirafik/v23-person.webm","bigWords":big}
P="/home/user/OpenMontage/remotion-composer/public/demo-props/"
json.dump(props,open(P+"jirafik-sotka23.json","w"),ensure_ascii=False,indent=1)
json.dump(dict(props,overlayOnly=True),open(P+"jirafik-sotka23-ovl.json","w"),ensure_ascii=False,indent=1)
print("vd",vd); print(jr)
