# YouTube cover 1920x1080: speaker on the right, navy gradient on the left with the title; no picture filters
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
src,out,hx=sys.argv[1],sys.argv[2],float(sys.argv[3])
F="/root/.fonts/"; W,H=1920,1080; NAVY=(20,24,58); ORANGE=(242,138,46); WHITE=(255,255,255)
russo=lambda s: ImageFont.truetype(F+"RussoOne-Regular.ttf",s)
def inter(s,w):
    f=ImageFont.truetype(F+"Inter-Variable.ttf",s)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
im=Image.open(src).convert("RGB")
z=1.35; cw,ch=int(3840/z),int(2160/z); x0=int(max(0,min(3840-cw,hx-0.70*cw)))
im=im.crop((x0,0,x0+cw,ch)).resize((W,H),Image.LANCZOS).convert("RGBA")
g=Image.new("L",(W,1))
for x in range(W): g.putpixel((x,0),int(max(0,min(1,(1150-x)/560))**0.9*235))
im=Image.composite(Image.new("RGBA",(W,H),NAVY+(255,)),im,g.resize((W,H)))
d=ImageDraw.Draw(im)
f1=russo(150); d.text((90,170),"8 БАНКОВ",font=f1,fill=WHITE); w2=d.textbbox((0,0),"71 000 ",font=f1)[2]; d.text((90,340),"71 000 ",font=f1,fill=ORANGE); d.text((90+w2,334),"₽",font=inter(150,"Black"),fill=ORANGE)
fp=russo(76); t="за 1 клиента"; tw=d.textbbox((0,0),t,font=fp)[2]
y=590; px=90; pw=tw+70
sh=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((px,y+12,px+pw,y+132),26,fill=(0,0,0,120)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
d=ImageDraw.Draw(im); d.rounded_rectangle((px,y,px+pw,y+120),26,fill=ORANGE); d.text((px+35,y+18),t,font=fp,fill=WHITE)
d.text((px+4,y+150),"ставки и условия всех офферов",font=inter(52,"ExtraBold"),fill=WHITE)
im.convert("RGB").save(out,quality=92)
