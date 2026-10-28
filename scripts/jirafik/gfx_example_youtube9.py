# cards (PIL PNGs) + subtitles (ASS) + final mix for the 16:9 YouTube cut
import json, re, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1920,1080; NAVY=(20,24,58); ORANGE=(242,138,46); WHITE=(255,255,255); GREY=(90,96,128)
F="/root/.fonts/"
def inter(size,w="ExtraBold"):
    f=ImageFont.truetype(F+"Inter-Variable.ttf",size)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
def russo(size): return ImageFont.truetype(F+"RussoOne-Regular.ttf",size)
def money(d,xy,value,size,fill,anchor="la"):
    # Russo One has no ruble sign: digits in Russo One, "₽" in Inter Black
    fa=russo(size); fr=inter(int(size*0.92),"Black")
    a=value.replace("₽","").rstrip(); has="₽" in value
    wa=d.textbbox((0,0),a,font=fa)[2]; wr=(d.textbbox((0,0),"₽",font=fr)[2]+int(size*0.18)) if has else 0
    x,y=xy
    neg=a.startswith("−"); a=a.lstrip("−")
    wa=d.textbbox((0,0),a,font=fa)[2]; wm=(d.textbbox((0,0),"−",font=fr)[2]+int(size*0.08)) if neg else 0
    if anchor[0]=="r": x-=wa+wr+wm
    if neg: d.text((x,y+int(size*0.04)),"−",font=fr,fill=fill); x+=wm
    d.text((x,y),a,font=fa,fill=fill)
    if has: d.text((x+wa+int(size*0.18),y+int(size*0.04)),"₽",font=fr,fill=fill)
    return wa+wr+wm
T=json.load(open("b/tokens_fixed.json")); C=json.load(open("b/cutlist.json"))
def norm(s): return re.sub(r"[^\wё ]","",s.lower().replace("ё","е"))
words=[norm(t["text"]) for t in T]
def at(phrase):
    p=norm(phrase).split()
    for i in range(len(words)-len(p)+1):
        if words[i:i+len(p)]==p: return T[i]["start"]
    raise KeyError(phrase)
def cut_t(t):
    for (a,b),o in zip(C["pieces"],C["off"]):
        if t<a: return o
        if a<=t<b: return o+(t-a)
    return C["total"]
os.makedirs("b/cards",exist_ok=True)
def canvas(): return Image.new("RGBA",(W,H),(0,0,0,0))
def shadowed(im,box,r):
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(sh)
    d.rounded_rectangle((box[0],box[1]+10,box[2],box[3]+10),r,fill=(10,12,30,95))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
def tw(d,s,f): l,t,r,b=d.textbbox((0,0),s,font=f); return r-l
def wrap(d,s,f,maxw):
    out=[];line=""
    for w in s.split():
        if line and tw(d,line+" "+w,f)>maxw: out.append(line); line=w
        else: line=(line+" "+w).strip()
    if line: out.append(line)
    return out
def chip(kicker,title):
    im=canvas(); d=ImageDraw.Draw(im); fk=inter(40,"ExtraBold"); ft=inter(46,"ExtraBold")
    x,y=64,56; kw=tw(d,kicker,fk)+48; tw_=tw(d,title,ft)+56; h=86
    shadowed(im,(x,y,x+kw+tw_,y+h),20); d=ImageDraw.Draw(im)
    d.rounded_rectangle((x,y,x+kw+tw_,y+h),20,fill=WHITE+(245,)); d.rounded_rectangle((x,y,x+kw,y+h),20,fill=ORANGE); d.rectangle((x+kw-20,y,x+kw,y+h),fill=ORANGE)
    d.text((x+24,y+h/2),kicker,font=fk,fill=WHITE,anchor="lm"); d.text((x+kw+28,y+h/2),title,font=ft,fill=NAVY,anchor="lm")
    im.info["kind"]="chip"
    return im
def stat(value,caption,y=300):
    im=canvas(); d=ImageDraw.Draw(im); fv=russo(96); fc=inter(36,"SemiBold")
    lines=wrap(d,caption,fc,560); vw=tw(d,value.replace("₽",""),fv)+(80 if "₽" in value else 0); w=max(vw,max(tw(d,l,fc) for l in lines))+80; h=150+len(lines)*46
    x1=W-70; x0=x1-w
    shadowed(im,(x0,y,x1,y+h),28); d=ImageDraw.Draw(im)
    d.rounded_rectangle((x0,y,x1,y+h),28,fill=WHITE+(245,))
    money(d,(x0+40,y+28),value,96,ORANGE)
    for i,l in enumerate(lines): d.text((x0+40,y+140+i*46),l,font=fc,fill=NAVY)
    return im
def table(title,rows,n,total=None):
    im=canvas(); d=ImageDraw.Draw(im); ft=inter(38,"ExtraBold"); fn=inter(36,"Bold"); fvv=inter(36,"ExtraBold"); fs=inter(26,"Medium"); ftot=russo(46)
    x0,x1,y=1210,W-60,110; rh=74
    h=80+n*rh+(96 if total else 0)+10
    shadowed(im,(x0,y,x1,y+h),28); d=ImageDraw.Draw(im)
    d.rounded_rectangle((x0,y,x1,y+h),28,fill=WHITE+(246,))
    d.text((x0+36,y+24),title,font=ft,fill=NAVY)
    yy=y+84
    for i,(name,val,sub) in enumerate(rows[:n]):
        if i: d.line((x0+36,yy-6,x1-36,yy-6),fill=(225,228,238),width=2)
        d.text((x0+36,yy),name,font=fn,fill=NAVY); d.text((x1-36,yy),val,font=fvv,fill=ORANGE,anchor="ra")
        if sub: d.text((x0+36,yy+40),sub,font=fs,fill=GREY)
        yy+=rh
    if total:
        d.rounded_rectangle((x0+24,yy+4,x1-24,yy+84),18,fill=NAVY)
        d.text((x0+52,yy+44),total[0],font=inter(30,"SemiBold"),fill=WHITE,anchor="lm"); d.text((x1-52,yy+44),total[1],font=inter(40,"ExtraBold"),fill=ORANGE,anchor="rm")
    return im
def steps(title,items,n):
    im=canvas(); d=ImageDraw.Draw(im); ft=inter(38,"ExtraBold"); fi=inter(34,"Bold"); fnum=inter(30,"ExtraBold")
    x0,x1,y=1230,W-60,120; rh=86; h=84+n*rh+10
    shadowed(im,(x0,y,x1,y+h),28); d=ImageDraw.Draw(im)
    d.rounded_rectangle((x0,y,x1,y+h),28,fill=WHITE+(246,)); d.text((x0+36,y+24),title,font=ft,fill=NAVY)
    yy=y+92
    for i,s in enumerate(items[:n]):
        last=i==n-1
        d.ellipse((x0+36,yy,x0+92,yy+56),fill=ORANGE if last else NAVY); d.text((x0+64,yy+28),str(i+1),font=fnum,fill=WHITE,anchor="mm")
        lines=wrap(d,s,fi,x1-x0-150)
        for k,l in enumerate(lines[:2]): d.text((x0+112,yy+28+(k-(len(lines[:2])-1)/2)*38),l,font=fi,fill=NAVY if last else (70,76,110),anchor="lm")
        if i<n-1: d.line((x0+64,yy+58,x0+64,yy+rh-2),fill=(200,204,220),width=4)
        yy+=rh
    return im
def cta():
    im=canvas(); d=ImageDraw.Draw(im); f1=inter(40,"SemiBold"); f2=russo(70)
    x1=W-70; x0=x1-840; y=300; h=230
    shadowed(im,(x0,y,x1,y+h),30); d=ImageDraw.Draw(im)
    d.rounded_rectangle((x0,y,x1,y+h),30,fill=NAVY+(248,))
    d.text((x0+44,y+40),"Бесплатное обучение — в Telegram",font=inter(38,"SemiBold"),fill=WHITE); d.text((x0+44,y+110),"@jirafiktrafik",font=f2,fill=ORANGE)
    return im
S=[]   # (png, start, end, fade_in, fade_out)
def add(img,t0,t1,fi=True,fo=True):
    p=f"b/cards/c{len(S):03d}.png"; kind=img.info.get("kind","card"); img.save(p); S.append((p,cut_t(t0),cut_t(t1),fi,fo,kind))
add(stat("РКО","ниша, где можно зарабатывать от 150 до 200 тыс. ₽ в месяц"),at("Ниша называется РКО"),at("Ниша называется РКО")+6)
add(chip("01","Кто я"),at("Меня зовут Илья"),at("Меня зовут Илья")+4)
add(stat("−600 000 ₽","прогорел на офлайн-магазине"),at("прогорел на"),at("прогорел на")+5)
add(chip("02","Мои результаты"),at("Теперь коротко о моих результатах"),at("Теперь коротко о моих результатах")+4)
add(stat("от 200 000 ₽","в месяц стабильно — больше года в РКО"),at("от 200 тысяч рублей в месяц"),at("полмиллиона")-0.3)
add(stat("500 000 ₽","за первый месяц — на двоих с другом"),at("полмиллиона"),at("полмиллиона")+5.5)
add(chip("03","Что такое РКО"),at("Сейчас объясню"),at("Сейчас объясню")+4)
add(stat("РКО","расчётно-кассовое обслуживание — счёт для бизнеса"),at("Сейчас объясню")+1.2,at("Сейчас объясню")+8)
add(stat("14 000 ₽","Альфа-Банк платит просто за открытие счёта"),at("Альфа платит 14"),at("Альфа платит 14")+5)
add(chip("04","Где брать такие ставки"),at("В своих коротких видео"),at("В своих коротких видео")+4.5)
add(stat("Партнёрская сеть","ставки выше, заявки без лимита и без срезов"),at("партнерскую сеть"),at("Теперь давайте поговорим о цифрах")-0.5)
add(chip("05","Цифры: 6 банков"),at("Теперь давайте поговорим о цифрах"),at("Теперь давайте поговорим о цифрах")+4.5)
rows=[("Альфа-Банк","14 000 ₽","за открытие счёта"),("Ozon Банк","8 000 ₽","клиент минимально активен"),("ВТБ","8 000 ₽","пополнить на 5 000 ₽, подержать сутки"),
      ("Т-Банк","10–20 тыс. ₽","продажа от 3 500 ₽"),("Сбербанк","4 000 ₽","+3 000 ₽ клиенту · транзакция от 1 000 ₽"),("ПСБ","9 000 ₽","платный тариф · бизнесу от 4 мес."),
      ("Симка Билайн","+6 000 ₽","оплата тарифа · ИП на Госуслугах")]
rt=[at("Как я говорил"),at("Вторым у нас идет"),at("Следующий по списку"),at("Четвертым у нас идет"),at("Это Сбербанк"),at("завершает наш открут")]
tend=at("как выглядит путь клиента")-0.3; tot=("С одного клиента","53–63 тыс. ₽")
for i in range(6): add(table("Офферы за одного клиента",rows,i+1),rt[i],rt[i+1] if i<5 else at("При таком раскладе"),fi=(i==0),fo=False)
add(table("Офферы за одного клиента",rows,6,tot),at("При таком раскладе"),at("За Билайн"),fi=False,fo=False)
add(table("Офферы за одного клиента",rows,7,tot),at("За Билайн"),tend,fi=False,fo=True)
add(chip("06","Путь клиента"),at("как выглядит путь клиента"),at("как выглядит путь клиента")+4)
st=["Источник трафика — находим клиента","Самозанятость в «Мой налог»","Заявка на ИП и встреча с представителем","Проверка налоговой 3–5 дней","Открываем расчётные счета","Выполняем целевое действие","Холд 14–30 дней → выплата"]
stt=[at("Для начала нам надо разобраться"),at("сделать самозанятость"),at("заводить заявку"),at("3–5 рабочих дней"),at("подвязывать расчетные счета"),at("обязательно надо выполнить целевое"),at("начинает идти холд")]
for i in range(7): add(steps("Путь клиента",st,i+1),stt[i],stt[i+1] if i<6 else at("За это время мы с вами разобрались")+3,fi=(i==0),fo=(i==6))
add(chip("07","Ошибки новичков"),at("разберем основные ошибки"),at("Первая главная ошибка")-0.2)
mk=[("Ошибка 1","Гонка за ставками",at("Первая главная ошибка"),at("Следующая ошибка похожая")),("Ошибка 2","Не выполнили целевое действие",at("Следующая ошибка похожая"),at("Третья ошибка")),
    ("Ошибка 3","Не дождались холда",at("Третья ошибка"),at("к ряду ошибок можно отнести")),("Ошибка 4","Кабинет банка вместо партнёрской сети",at("к ряду ошибок можно отнести"),at("Также бывает такое")),
    ("Ошибка 5","Не оформили самозанятость",at("Также бывает такое"),at("последней ошибкой")),("Ошибка 6","Не тот источник трафика",at("последней ошибкой"),at("Если ты хочешь глубже"))]
for k,ti,a,b in mk: add(chip(k,ti),a,b-0.2)
add(stat("ОТП: 11 000 ₽","но нужен оборот клиента от 2 млн ₽"),at("ОТП Банк"),at("ОТП Банк")+9)
add(stat("≈60 000 ₽","в год — страховые взносы, если выбрать не тот режим"),at("60 тысяч в год")-1.5,at("60 тысяч в год")+6)
add(cta(),at("Если ты хочешь глубже"),C["total"]+5)
json.dump(S,open("b/cards.json","w"))
# subtitles: phrases of up to ~6 words / 42 chars, split at pauses and sentence ends
def ts(t): t=max(0,t); return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
ev=[];cur=[]
toks=[{**t,"cs":cut_t(t["start"]),"ce":cut_t(t["end"])} for t in T]
for i,t in enumerate(toks):
    cur.append(t); txt=" ".join(x["text"] for x in cur)
    nxt=toks[i+1] if i+1<len(toks) else None
    gap=(nxt["start"]-t["end"]) if nxt else 9
    glue=re.fullmatch(r"(до|от|на|в|во|с|со|и|а|но|по|за|к|о|об|у|не|из|для|что|как|это|—|\d[\d ]*)",t["text"].lower()) is not None
    if not nxt or gap>0.45 or re.search(r"[.!?…]$",t["text"]) or (len(txt)>40 and not (glue and len(txt)<52)) or (re.search(r"[,:—]$",t["text"]) and len(txt)>22):
        ev.append((cur[0]["cs"],t["ce"]+0.25 if not nxt else min(t["ce"]+0.35,nxt["cs"]),txt)); cur=[]
ass=["[Script Info]","ScriptType: v4.00+","PlayResX: 1920","PlayResY: 1080","WrapStyle: 0","","[V4+ Styles]",
"Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
"Style: Sub,Inter,52,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,3.2,1.5,2,200,200,64,1","","[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for a,b,txt in ev:
    if b-a<0.25: b=a+0.25
    txt=txt.rstrip(",").replace("...","…")
    ass.append(f"Dialogue: 0,{ts(a)},{ts(b)},Sub,,0,0,0,,{{\\fad(80,60)}}{txt}")
open("b/subs.ass","w").write("\n".join(ass)+"\n")
print("cards",len(S),"subs",len(ev))
