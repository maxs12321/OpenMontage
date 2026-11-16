# vertical cover 1080x1920 from a (tone-mapped) frame: orange title plate + white second plate, no picture filters
# usage: cover_vertical.py frame.png out.jpg "line 1" "line 2"
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
src,out,l1,l2=sys.argv[1:5]
F="/root/.fonts/"; NAVY=(20,24,58); ORANGE=(242,138,46); WHITE=(255,255,255)
im=Image.open(src).convert("RGB").resize((1080,1920),Image.LANCZOS); W,H=im.size
def fit(t,mx,size):
    d=ImageDraw.Draw(im)
    while True:
        f=ImageFont.truetype(F+"RussoOne-Regular.ttf",size); l,_,r,_=d.textbbox((0,0),t,font=f)
        if r-l<=mx: return f
        size-=4
def plate(text,font,y,bg,fg,pad=(44,20),r=28):
    # Russo One has no ruble sign: a trailing "₽" is drawn in Inter Black
    global im
    rub=text.endswith("₽"); text=text[:-1].rstrip() if rub else text
    fr=ImageFont.truetype(F+"Inter-Variable.ttf",int(font.size*0.95))
    try: fr.set_variation_by_name("Black")
    except Exception: pass
    d=ImageDraw.Draw(im); l,t,rr,b=d.textbbox((0,0),text,font=font); gap=int(font.size*0.22); wr=(d.textbbox((0,0),"₽",font=fr)[2]+gap) if rub else 0
    w,h=rr-l+wr,b-t; x=(W-w)//2
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle((x-pad[0],y+10,x+w+pad[0],y+h+2*pad[1]+10),r,fill=(0,0,0,90))
    im=Image.alpha_composite(im.convert("RGBA"),sh.filter(ImageFilter.GaussianBlur(14))).convert("RGB")
    d=ImageDraw.Draw(im); d.rounded_rectangle((x-pad[0],y,x+w+pad[0],y+h+2*pad[1]),r,fill=bg); d.text((x-l,y+pad[1]-t),text,font=font,fill=fg)
    if rub: d.text((x+rr-l+gap,y+pad[1]-t+int(font.size*0.02)),"₽",font=fr,fill=fg)
    return y+h+2*pad[1]
y=plate(l1,fit(l1,900,190),300,ORANGE,WHITE,pad=(50,24),r=30)
plate(l2,fit(l2,860,130),y+26,WHITE,NAVY)
im.save(out,quality=95)
