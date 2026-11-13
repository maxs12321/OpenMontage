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
add(chip("01","Кто я"),at("Кто я и почему"),at("Кто я и почему")+4)
add(stat("1 год","в нише РКО: в команде отвечаю за трафик и техническую часть"),at("Меня зовут Илья"),at("Все что расскажу")-0.3,side=A)
add(chip("02","Источник 1 — Окружение"),at("Источник первый"),at("Источник первый")+4.5)
add(stat("Окружение","те, кто работает на себя: мебель, выпечка, услуги, самозанятые"),at("Люди вокруг тебя"),at("Почему это лучший старт")-0.3,side=A)
add(stat("Лучший старт","человек тебя знает — не нужно доказывать, что ты не мошенник"),at("Почему это лучший старт"),at("Но здесь смысл")-0.3,side=A)
add(stat("Это тренировка","узнаёшь частые вопросы и механику регистрации в банках"),at("Смысл в том чтобы понять"),at("И сразу скажу")-0.3,side=A)
add(stat("Важно","ИП открывают для себя: пользуется сам, доступы остаются у него"),at("Человек открывает ИП для себя"),at("Это не работа с клиентом")+1.5,side=A)
add(chip("03","Источник 2 — Бухгалтеры"),at("Теперь переходим к холодным"),at("Теперь переходим к холодным")+4.5)
st=["Найти бухгалтера","Предложить сотрудничество","Рассказать про ставки за банки","Клиенту нужен счёт — даёте реф. ссылку","После холда делите прибыль"]
stt=[at("Найти бухгалтера"),at("предложить ему формат"),at("рассказать про ставки"),at("у кого попросить реферальную"),at("делите прибыль")]
for i in range(5): add(steps("Работа с бухгалтером",st,i+1),stt[i],stt[i+1] if i<4 else at("делите прибыль")+5,fi=(i==0),fo=(i==4),side=("g",stt[0]))
add(chip("04","Источник 3 — Эксперты и онлайн-школы"),at("Все ведь знают"),at("Все ведь знают")+4.5)
add(stat("ИП на НПД","те же 4–6 % налога, без страховых взносов; счёт первые 2–3 мес. бесплатно, дальше 500 ₽/мес"),at("в плане условий"),at("Давайте разберем почему выгодно")-0.3,side=A)
pl=["Статус ИП и расчётный счёт","Заказы от крупных компаний","Безопаснее принимать деньги","Меньше рисков по 115-ФЗ"]
plt=[at("Для ученика статус"),at("Самый главный плюс"),at("на который безопаснее"),at("Также сам ученик")]
for i in range(4): add(steps("Плюсы для ученика",pl,i+1),plt[i],plt[i+1] if i<3 else at("Если дальше копаться")+1,fi=(i==0),fo=(i==3),side=("g",plt[0]))
add(stat("Выгода эксперту","дополнительный заработок по реферальной программе"),at("Ну а для вас"),at("Теперь я скажу")-0.3,side=A)
add(chip("05","Что сработало хуже"),at("Теперь я скажу"),at("Теперь я скажу")+4.5)
add(stat("Запасные счета","для ИП: у нас не клеился диалог, но инструмент рабочий"),at("Это предлагать индивидуальным"),at("Какой источник выбрать")-0.3,side=A)
add(chip("06","Какой источник выбрать"),at("Какой источник выбрать"),at("Какой источник выбрать")+4.5)
ch=["Нет опыта — окружение","Готов общаться — холодные связки","Выбирай то, что сможешь делать регулярно"]
cht=[at("Нет опыта"),at("Готов писать"),at("Выбираешь то")]
for i in range(3): add(steps("Простое правило",ch,i+1),cht[i],cht[i+1] if i<2 else at("Цифры которые назвал"),fi=(i==0),fo=(i==2),side=("g",cht[0]))
add(cta(),at("есть бесплатное обучение"),C["total"]+5,side=A)
os.makedirs("b/cards",exist_ok=True); flush()
json.dump(S,open("b/cards.json","w"))
exec(sub)
# drawn on the 4K layer directly: libass does not scale PlayRes here, so the script is written at 3840x2160
s=open("b/subs.ass").read().replace("PlayResX: 1920","PlayResX: 3840").replace("PlayResY: 1080","PlayResY: 2160").replace(
 "Style: Sub,Inter,52,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,3.2,1.5,2,200,200,64,1",
 "Style: Sub,Inter,200,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,10,5,2,400,400,150,1")
open("b/subs.ass","w").write(s)
