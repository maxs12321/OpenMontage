# cards (PIL PNGs) + subtitles (ASS) + final mix for the 16:9 YouTube cut
import json, re, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1920,1080; K=2   # layout in 1080p units, drawn at 4K
NAVY=(20,24,58); ORANGE=(242,138,46); WHITE=(255,255,255); GREY=(90,96,128)
F="/root/.fonts/"
def inter(size,w="ExtraBold"):
    f=ImageFont.truetype(F+"Inter-Variable.ttf",int(size*K))
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
def russo(size): return ImageFont.truetype(F+"RussoOne-Regular.ttf",int(size*K))
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

class SD:
    """ImageDraw in 1080p coordinates on a 4K canvas"""
    def __init__(s,im): s.d=ImageDraw.Draw(im)
    def textbbox(s,xy,text,font,**k): return tuple(v/K for v in s.d.textbbox((xy[0]*K,xy[1]*K),text,font=font,**k))
    def text(s,xy,text,font=None,fill=None,anchor=None): s.d.text((xy[0]*K,xy[1]*K),text,font=font,fill=fill,anchor=anchor)
    def rounded_rectangle(s,box,r,fill=None): s.d.rounded_rectangle(tuple(v*K for v in box),r*K,fill=fill)
    def rectangle(s,box,fill=None): s.d.rectangle(tuple(v*K for v in box),fill=fill)
    def ellipse(s,box,fill=None): s.d.ellipse(tuple(v*K for v in box),fill=fill)
    def line(s,xy,fill=None,width=1): s.d.line(tuple(v*K for v in xy),fill=fill,width=int(width*K))
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
def canvas(): return Image.new("RGBA",(W*K,H*K),(0,0,0,0))
def shadowed(im,box,r):
    sh=Image.new("RGBA",(W*K,H*K),(0,0,0,0)); d=SD(sh)
    d.rounded_rectangle((box[0],box[1]+10,box[2],box[3]+10),r,fill=(10,12,30,95))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16*K)))
def tw(d,s,f): l,t,r,b=d.textbbox((0,0),s,font=f); return r-l
def wrap(d,s,f,maxw):
    out=[];line=""
    for w in s.split():
        if line and tw(d,line+" "+w,f)>maxw: out.append(line); line=w
        else: line=(line+" "+w).strip()
    if line: out.append(line)
    return out
def chip(kicker,title):
    im=canvas(); d=SD(im); fk=inter(40,"ExtraBold"); ft=inter(46,"ExtraBold")
    x,y=64,56; kw=tw(d,kicker,fk)+48; tw_=tw(d,title,ft)+56; h=86
    shadowed(im,(x,y,x+kw+tw_,y+h),20); d=SD(im)
    d.rounded_rectangle((x,y,x+kw+tw_,y+h),20,fill=WHITE+(245,)); d.rounded_rectangle((x,y,x+kw,y+h),20,fill=ORANGE); d.rectangle((x+kw-20,y,x+kw,y+h),fill=ORANGE)
    d.text((x+24,y+h/2),kicker,font=fk,fill=WHITE,anchor="lm"); d.text((x+kw+28,y+h/2),title,font=ft,fill=NAVY,anchor="lm")
    im.info["kind"]="chip"
    return im
def stat(value,caption,y=300):
    # kept right of the face (he sits in the centre): card no wider than 640 px from x=1210
    im=canvas(); d=SD(im); MAXW=640; fs=96
    while True:
        fv=russo(fs); vw=tw(d,value.replace("₽",""),fv)+(int(fs*0.85) if "₽" in value else 0)
        if vw<=MAXW-80 or fs<=56: break
        fs-=4
    fc=inter(36,"SemiBold"); lines=wrap(d,caption,fc,MAXW-80)
    w=min(MAXW,max(vw,max(tw(d,l,fc) for l in lines))+80); h=int(fs*1.45)+len(lines)*46+14
    x1=W-70; x0=x1-w
    shadowed(im,(x0,y,x1,y+h),28); d=SD(im)
    d.rounded_rectangle((x0,y,x1,y+h),28,fill=WHITE+(245,))
    money(d,(x0+40,y+28),value,fs,ORANGE)
    for i,l in enumerate(lines): d.text((x0+40,y+int(fs*1.45)+i*46),l,font=fc,fill=NAVY)
    return im
def table(title,rows,n,total=None):
    im=canvas(); d=SD(im); ft=inter(38,"ExtraBold"); fn=inter(36,"Bold"); fvv=inter(36,"ExtraBold"); fs=inter(26,"Medium"); ftot=russo(46)
    x0,x1,y=1210,W-60,110; rh=74
    h=80+n*rh+(96 if total else 0)+10
    shadowed(im,(x0,y,x1,y+h),28); d=SD(im)
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
    im=canvas(); d=SD(im); ft=inter(38,"ExtraBold"); fi=inter(34,"Bold"); fnum=inter(30,"ExtraBold")
    x0,x1,y=1230,W-60,120; rh=86; h=84+n*rh+10
    shadowed(im,(x0,y,x1,y+h),28); d=SD(im)
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
    im=canvas(); d=SD(im); f2=russo(66)
    x1=W-70; x0=x1-640; y=300; h=270
    shadowed(im,(x0,y,x1,y+h),30); d=SD(im)
    d.rounded_rectangle((x0,y,x1,y+h),30,fill=NAVY+(248,))
    d.text((x0+44,y+38),"Бесплатное обучение",font=inter(40,"SemiBold"),fill=WHITE); d.text((x0+44,y+90),"в Telegram",font=inter(40,"SemiBold"),fill=WHITE)
    d.text((x0+44,y+158),"@jirafiktrafik",font=f2,fill=ORANGE)
    return im
S=[]   # (png, start, end, fade_in, fade_out, kind)
def add(img,t0,t1,fi=True,fo=True):
    p=f"b/cards/c{len(S):03d}.png"; kind=img.info.get("kind","card"); img.save(p); S.append((p,cut_t(t0),cut_t(t1),fi,fo,kind))
add(chip("01","Кто я"),at("Меня зовут Илья"),at("Меня зовут Илья")+4)
add(stat("250 000 ₽","каждому из нас за первые полтора месяца — на двоих с другом"),at("на двоих с другом"),at("на двоих с другом")+6)
add(stat("−200…250 тыс. ₽","потеряли на оффере Газпрома: не выполнили условия банка"),at("абсолютно все до нуля потеряли")-1.5,at("абсолютно все до нуля потеряли")+6)
add(chip("02","Шаг 1 — ИП на НПД"),at("теперь приступим к практике"),at("теперь приступим к практике")+4.5)
add(stat("ИП на НПД","те же 4–6 % налога, без страховых взносов и отчётности"),at("Мы открываем ИП на НПД"),at("Никаких отчетностей")+3)
st=["Самозанятость в «Мой налог» — 30–40 минут","Онлайн-заявка на ИП в любой банк","Встреча с представителем, подпись документов","Ждём 3–5 рабочих дней","Пользуемся счётом или подвязываем другие банки"]
stt=[at("Сначала регистрируем самозанятость"),at("Подаем онлайн заявку"),at("Встречаемся с представителем"),at("ждем 3-5 рабочих дней"),at("пользоваться тем же самым счетом")]
for i in range(5): add(steps("Как открыть ИП на НПД",st,i+1),stt[i],stt[i+1] if i<4 else at("Ну и закрывается ИП"),fi=(i==0),fo=(i==4))
add(chip("03","Шаг 2 — Партнёрская сеть"),at("Именно поэтому мы в работе используем"),at("Именно поэтому мы в работе используем")+4.5)
add(stat("Партнёрская сеть","посредник между тобой и банком: офферы, ставки и личный менеджер"),at("Партнерская сеть это посредник"),at("Третий и очень важный шаг")-0.5)
add(chip("04","Шаг 3 — Открутить себя"),at("Третий и очень важный шаг"),at("Третий и очень важный шаг")+4.5)
rows=[("Альфа-Банк","11 000 ₽","ИП на НПД"),("Т-Банк","10–20 тыс. ₽",""),("Ozon Банк","8 000 ₽",""),("ПСБ","9 000 ₽","ИП открыт больше 4 мес."),("Сбербанк","4 000 ₽",""),("ВТБ","8 000 ₽",""),("Симка Билайн","+6 000 ₽","корпоративная")]
rt=[at("На данный момент Альфа-банк"),at("Т-банк платит"),at("Озон платит"),at("ПСБ платит"),at("Сбербанк платит"),at("и ВТБ"),at("корпоративную симку")]
tend=at("Но самое главное из этого всего")+4; tot=("С одного клиента","от 56 000 ₽")
for i in range(6): add(table("Сколько платят банки",rows,i+1),rt[i],rt[i+1],fi=(i==0),fo=False)
add(table("Сколько платят банки",rows,7,tot),rt[6],tend,fi=False,fo=True)
add(stat("Целевое действие","условие банка, за которое он платит по реферальной программе"),at("целевое действие это"),at("целевое действие это")+7)
add(chip("05","Шаг 4 — Ищем клиентов"),at("Шаг 4"),at("Шаг 4")+4.5)
add(stat("Не нужны обороты","лучше человек, который только начинает своё дело"),at("Главное заблуждение новичка"),at("Главное заблуждение новичка")+8)
add(stat("Пример: дизайнер","самозанятый → ИП на НПД: крупные клиенты, меньше блокировок по 115-ФЗ"),at("Можно найти какого-нибудь дизайнера"),at("По итогу дизайнер получит")+4)
add(chip("06","Где отваливаются новички"),at("на каких этапах отваливаются новички"),at("на каких этапах отваливаются новички")+4.5)
mk=[("Ошибка 1","Пугает холд 14–30 дней",at("на такой волне"),at("Также некоторые не до конца")),
    ("Ошибка 2","Не дочитали условия банка",at("Также некоторые не до конца"),at("Также бывает такое")),
    ("Ошибка 3","Не та связка",at("самая главная ошибка"),at("В целом вот такой вот путь"))]
for k,ti,a,b in mk: add(chip(k,ti),a,b-0.2)
add(cta(),at("я даю бесплатное обучение"),C["total"]+5)
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
