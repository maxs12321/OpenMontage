# YouTube cards + subtitles for "где искать первых клиентов" (same look as the "путь с нуля" video)
import json, re, os, subprocess
src=open("/home/user/OpenMontage/scripts/jirafik/yt14_gfx.py").read()
head=src.split("S=[]   #")[0].replace('json.load(open("b/tokens_fixed.json"))','json.load(open("b/tokens_final.json"))')
exec(head)                       # helpers: canvas, chip, stat, table, steps, cta, at, cut_t ...
sub=src.split("json.dump(S,open(\"b/cards.json\",\"w\"))")[1]   # subtitle block, reused as is
from PIL import Image
S=[]; LATER=[]
def add(img,t0,t1,fi=True,fo=True,side="r"):
    LATER.append((img,t0,t1,fi,fo,side))
def flush():
    key=lambda t0,s: round((t0 if s=="auto" else s[1])+1.0,2)
    ts=sorted({key(t0,s) for _,t0,_,_,_,s in LATER if s!="r"})
    pos=json.loads(subprocess.check_output(["/home/user/OpenMontage/.venv/bin/python","-I","facepos.py","raw/src.mov",json.dumps(ts)]).decode()) if ts else {}
    for img,t0,t1,fi,fo,side in LATER:
        if side!="r":
            x=pos[str(key(t0,side))]; side="l" if x>0.5 else "r"
        if side=="l":   # mirror the card to the left edge (the speaker sits right of centre here)
            bb=img.getbbox()
            if bb:
                sh=Image.new("RGBA",img.size,(0,0,0,0)); sh.alpha_composite(img.crop(bb),(40*K,bb[1])); img=sh
        p=f"b/cards/c{len(S):03d}.png"; kind=img.info.get("kind","card"); img.save(p); S.append((p,cut_t(t0),cut_t(t1),fi,fo,kind))
A="auto"
# all times below are source seconds (cut_t maps them through the cut list)
add(stat("8 банков = 71 000 ₽","столько в сумме платят за одного клиента"),0.3,10.5,side=A)
add(chip("01","Кто я"),at("Меня зовут Илья"),at("Меня зовут Илья")+4)
add(chip("02","За что платит банк"),at("Прежде чем пойду"),at("Прежде чем пойду")+4.5)
add(stat("Целевое действие","банк чаще платит не за открытие счёта, а за тариф, пополнение или платёж"),at("Банк платит не за открытие"),145.3,side=A)
B=[("1/8","Озон Банк — 5 000 ₽",146.27),("2/8","РСХБ — 7 000 ₽",229.6),("3/8","ВТБ — 8 000 ₽",264.26),("4/8","Т-Банк — 10 000 ₽",308.77),
   ("5/8","Сбербанк — 10 000 ₽",379.91),("6/8","ПСБ — 11 000 ₽",485.89),("7/8","Альфа-Банк — 11–14 тыс. ₽",520.75),("8/8","Симка Билайн — 6 000 ₽",555.12)]
for k,ti,t in B: add(chip(k,ti),t,t+5)
add(stat("5 000 ₽","Озон Банк через личный кабинет: пополнить счёт на 1 000 ₽"),at("Целевое действие довольно простое"),224.5,side=A)
add(stat("10 человек в месяц","лимит на один личный кабинет Озон Банка"),224.75,229.4,side=A)
add(stat("7 000 ₽","РСХБ: счёт на платном тарифе, минимальный — 650 ₽ в месяц"),at("Минимальный тариф")-1.5,249.8,side=A)
add(stat("Не во всех городах","РСХБ есть не везде"),249.95,256.5,side=A)
add(stat("8 000 ₽","ВТБ: пополнить счёт на 5 000 ₽ и подержать сутки"),266.5,284.9,side=A)
add(stat("Минус ВТБ","представители могут перехватить заявку; отказ приходит сразу"),285.05,307.5,side=A)
add(stat("10 000 ₽","Т-Банк: пополнение счёта от 3 500 ₽, работаем с ИП на НПД"),310.52,335.6,side=A)
add(stat("До 20 000 ₽","«Т-Банк для бизнеса», только ИП на АУСН: пополнить 1 500 ₽, обменять в тенге и обратно"),351.7,379.6,side=A)
add(stat("10 000 ₽","Сбер: открытие счёта, бизнес от 30 дней, ИП на НПД не подходит"),382.0,414.9,side=A)
add(stat("4 000 ₽ + 3 000 ₽","«Сбер для бизнеса»: тебе и клиенту, перевод от 1 000 ₽, до 15 человек в год"),415.23,459.2,side=A)
add(stat("Важно","не сказал про личный кабинет — значит, работаем через партнёрскую сеть"),459.43,485.6,side=A)
add(stat("11 000 ₽","ПСБ: за открытие счёта, но иногда отказывают — по скорингу или после встречи"),488.0,518.0,side=A)
add(stat("11 000–14 000 ₽","Альфа-Банк: ИП на НПД — 11 000 ₽, ИП на АУСН — 14 000 ₽, за открытие счёта"),526.3,554.9,side=A)
add(stat("6 000 ₽","корпоративная симка Билайн: оплата тарифа + подтверждение на Госуслугах"),560.7,580.4,side=A)
add(chip("03","С чего начать новичку"),580.64,585.6)
add(stat("1–2 оффера","не хватайся за все 8: начни с тех, где нужно просто открыть счёт"),582.32,612.0,side=A)
nb=["Альфа-Банк","Сбер через «Сбер для бизнеса»","Озон Банк через личный кабинет","Симка Билайн"]
nbt=[612.4,620.46,624.76,643.07]
for i in range(4): add(steps("Что взять в работу",nb,i+1),nbt[i],nbt[i+1] if i<3 else 649.0,fi=(i==0),fo=(i==3),side=("g",nbt[0]))
rows=[("Озон Банк","5 000 ₽",""),("РСХБ","7 000 ₽",""),("ВТБ","8 000 ₽",""),("Т-Банк","10 000 ₽",""),("Сбербанк","10 000 ₽",""),("ПСБ","11 000 ₽",""),("Альфа-Банк","11–14 тыс. ₽",""),("Симка Билайн","6 000 ₽","")]
add(table("Все 8 офферов",rows,8),649.24,667.3,side=A)
add(cta(),667.53,C["total"]+5,side=A)
os.makedirs("b/cards",exist_ok=True); flush()
json.dump(S,open("b/cards.json","w"))
