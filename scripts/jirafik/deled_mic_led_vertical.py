# hide the mic's green status LED: inside the hand/mic zone, strongly green pixels (plus a soft halo) are
# pulled to a dark neutral like the mic body. The plant on the right is outside the zone.
import sys, subprocess, numpy as np
src, out = sys.argv[1], sys.argv[2]
START=float(sys.argv[3]) if len(sys.argv)>3 else 0.0
W,H=1080,1920; X0,X1,Y0,Y1=300,800,700,1600
rd=subprocess.Popen(["ffmpeg","-loglevel","error","-ss",f"{START:.4f}","-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
wr=subprocess.Popen(["ffmpeg","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","60","-i","-","-ss",f"{START:.4f}","-i",src,
  "-map","0:v","-map","1:a","-c:v","libx264","-crf","14","-preset","fast","-pix_fmt","yuv420p","-c:a","copy",out],stdin=subprocess.PIPE)
def blur(m,r):
    # cheap separable box blur for the mask halo
    k=np.ones(2*r+1,np.float32)/(2*r+1)
    m=np.apply_along_axis(lambda v: np.convolve(v,k,"same"),0,m)
    return np.apply_along_axis(lambda v: np.convolve(v,k,"same"),1,m)
n=0; hits=0
while True:
    buf=rd.stdout.read(W*H*3)
    if len(buf)<W*H*3: break
    f=np.frombuffer(buf,np.uint8).reshape(H,W,3).copy()
    z=f[Y0:Y1,X0:X1].astype(np.float32); R,G,B=z[...,0],z[...,1],z[...,2]
    core=(G>140)&((G-np.maximum(R,B))>55)   # bright LED green, not the darker green hoodie
    if core.any():
        hits+=1
        ys,xs=np.nonzero(core)
        cy,cx=np.median(ys),np.median(xs)
        y0,y1=max(0,int(cy)-30),min(Y1-Y0,int(cy)+31); x0,x1=max(0,int(cx)-30),min(X1-X0,int(cx)+31)
        keep=(ys>=y0)&(ys<y1)&(xs>=x0)&(xs<x1)          # the LED blob only, not stray green
        ys,xs=ys[keep],xs[keep]
        sub=z[y0:y1,x0:x1]; r,g,b=sub[...,0],sub[...,1],sub[...,2]
        c=np.zeros(sub.shape[:2],np.float32); c[ys-y0,xs-x0]=1
        near=blur(c,6)>0.02                                   # around the green glow
        hot=near&(np.minimum(np.minimum(r,g),b)>120)          # the over-exposed white core of the LED
        green=np.clip(((g-np.maximum(r,b))-12)/30,0,1)*near   # how green each pixel is
        mn=np.minimum(np.minimum(r,g),b)
        notshirt=np.where(hot,1.0,np.clip((175-mn)/70,0,1))  # the halo must not darken the white shirt next to the mic
        a=np.clip(np.maximum(green,blur((c+hot).clip(0,1),4)*1.8*notshirt),0,1)[...,None]
        dark=np.repeat((np.minimum(r,b)*0.06+26)[...,None],3,axis=2)   # neutral dark, like the mic body
        z[y0:y1,x0:x1]=sub*(1-a)+dark*a
        f[Y0:Y1,X0:X1]=np.clip(z,0,255).astype(np.uint8)
    wr.stdin.write(f.tobytes()); n+=1
    if n%3600==0: print(n,hits,flush=True)
wr.stdin.close(); wr.wait(); print("frames",n,"with LED",hits)
