import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
src,out=sys.argv[1],sys.argv[2]
F="/root/.fonts/"; W,H=1920,1080; NAVY=(20,24,58); ORANGE=(242,138,46); WHITE=(255,255,255)
def inter(s,w):
    f=ImageFont.truetype(F+"Inter-Variable.ttf",s)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
russo=lambda s: ImageFont.truetype(F+"RussoOne-Regular.ttf",s)
im=Image.open(src).convert("RGB")
s=1.4; cw,ch=int(W/s),int(H/s); x0=60
im=im.crop((x0,0,x0+cw,ch)).resize((W,H),Image.LANCZOS)
im=ImageEnhance.Contrast(im).enhance(1.06); im=ImageEnhance.Color(im).enhance(1.08)
im=im.filter(ImageFilter.UnsharpMask(radius=2,percent=60,threshold=2)).convert("RGBA")
# navy gradient from the left for the title
g=Image.new("L",(W,1))
for x in range(W): g.putpixel((x,0),int(max(0,min(1,(1260-x)/640))**0.9*240))
im=Image.composite(Image.new("RGBA",(W,H),NAVY+(255,)),im,g.resize((W,H)))
d=ImageDraw.Draw(im)
f1=russo(210); d.text((90,170),"НИША",font=f1,fill=WHITE); d.text((90,385),"РКО",font=f1,fill=ORANGE)
# price plate: digits in Russo One, ruble sign in Inter (Russo has no ₽)
fp=russo(92); fr=inter(86,"Black"); fs=inter(56,"ExtraBold")
a="150–200 тыс. "; wa=d.textbbox((0,0),a,font=fp)[2]; wr=d.textbbox((0,0),"₽",font=fr)[2]
y=650; px=90; pw=wa+wr+70
sh=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((px,y+12,px+pw,y+148),28,fill=(0,0,0,120)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
d=ImageDraw.Draw(im); d.rounded_rectangle((px,y,px+pw,y+136),28,fill=ORANGE)
d.text((px+35,y+18),a,font=fp,fill=WHITE); d.text((px+35+wa,y+24),"₽",font=fr,fill=WHITE)
d.text((px+4,y+170),"в месяц — из дома, с нуля",font=fs,fill=WHITE)
im.convert("RGB").save(out,quality=92)
