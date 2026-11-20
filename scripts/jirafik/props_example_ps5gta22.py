import json, subprocess, os
from PIL import ImageFont
d=json.load(open("timeline_n.json")); W=d["words"]
exec(open("build.py").read().split("words=[]")[0])   # pieces + mp() from the same cut list
def iw(i): return round(mp(g[i]["start"]),3)
vd=round(d["total"]-0.07,3)
notes=[{"start":iw(17)-0.05,"end":iw(28)-0.1,"text":"Бесплатный гайд по нише — в конце","top":380},
       {"start":iw(130),"end":iw(143)-0.1,"text":"Что такое РКО — видео закреплено в профиле","top":380}]
boards=[{"start":iw(28)-0.05,"end":iw(51)-0.1,"blocks":[
   {"at":iw(28),"icon":"bank","title":"8 банков","sub":"платят за одного и того же человека"},
   {"at":iw(44),"icon":"coins","title":"71 000 ₽","sub":"в сумме за одного клиента","tone":"good"}]},
  {"start":iw(51)-0.05,"end":iw(71)-0.1,"blocks":[
   {"at":iw(51),"icon":"bank","title":"Так выходит не всегда","sub":"где-то откажет банк, где-то клиент не выполнит условия","tone":"bad"}]},
  {"start":iw(71)-0.05,"end":iw(106)-0.1,"blocks":[
   {"at":iw(75),"icon":"doc","title":"71 000 ₽ ÷ 8 ≈ 9 000 ₽","sub":"в среднем за один оффер"},
   {"at":iw(92),"icon":"coins","title":"Половина = 35 000 ₽","sub":"офферов с одного человека","tone":"good"}]},
  {"start":iw(106)-0.05,"end":iw(121)-0.1,"blocks":[
   {"at":iw(106),"icon":"people","title":"2 клиента = 70 000 ₽","sub":"как раз PS5 + GTA 6","tone":"good"}]}]
a,b=round(iw(121)-0.05,3),round(iw(130)-0.1,3)
if not os.path.exists("b/person.webm"): subprocess.run(["/home/user/OpenMontage/.venv/bin/python","-I","/home/user/OpenMontage/scripts/jirafik/matte.py","b/cut_n.mp4","b/person.webm",str(a-0.5),str(b+0.5)],check=True)
f={"family":"'Russo One', sans-serif","weight":400,"lineHeight":0.95}
lines=["БАНКИ"]; size=420
while max(ImageFont.truetype("/root/.fonts/RussoOne-Regular.ttf",size).getlength(l) for l in lines)>740: size-=5
big=[{"start":a,"end":b,"lines":lines,"size":size,"top":700,"align":"center","font":f}]
cta={"start":iw(143),"end":vd,"label":"Бесплатное обучение — в Telegram","handle":"@jirafiktrafik"}
Z=0.22
CLOSE=[(iw(51)-0.08,iw(71)-0.05),(iw(106)-0.08,iw(121)-0.05),(iw(143)-0.08,vd)]
jr=[[round(s0,3),round(e0,3),Z,50.0,50.0] for s0,e0 in CLOSE]
props={"videoSrc":"jirafik/v22n-cut.mp4","videoDuration":vd,"fps":60,"cuts":d["cuts"],"whooshAt":[],"emphasis":[],
 "words":W,"stickers":[],"inserts":[],"chapters":[],"notes":notes,"cta":cta,"boards":boards,
 "hook":{"tag":"","line1":"PS5 + GTA 6","line2":"= 2 человека","until":round(iw(13)-0.05,3),"teaser":"РКО","size":110,"line2At":iw(5)-0.05},
 "hookStyle":"lower","captionStyle":"word","captionsFrom":round(iw(13)-0.05,3),"sfx":[],
 "endCard":{"seconds":0,"question":"","handles":[]},
 "motion":{"push":0.015,"jumpZoom":0.12,"jumpRanges":jr,"alternate":False,"punch":0,"blur":0,"flash":False,"emphasisZoom":0.05,"vignette":False},
 "transitions":[],"plateTheme":"light","showProgress":False,"personSrc":"jirafik/v22-person.webm","bigWords":big}
P="/home/user/OpenMontage/remotion-composer/public/demo-props/"
json.dump(props,open(P+"jirafik-ps5gta22.json","w"),ensure_ascii=False,indent=1)
json.dump(dict(props,overlayOnly=True),open(P+"jirafik-ps5gta22-ovl.json","w"),ensure_ascii=False,indent=1)
print("vd",vd); print(jr)
