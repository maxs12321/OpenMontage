import subprocess
TM="zscale=tin=arib-std-b67:pin=bt2020:min=bt2020nc:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,curves=all='0/0 0.5/0.56 1/1',colorchannelmixer=rr=0.98:gg=0.99:bb=1.09,eq=saturation=0.95"
PRE="scale=1080:1920:force_original_aspect_ratio=increase:force_divisible_by=2:flags=bicubic"
FIT="scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"
def blur(xexpr, until=None):
    en=f":enable='lt(t,{until})'" if until else ""
    # hide the client column (name + INN); the camera pans, so the box follows it
    return f",split[o][b];[b]crop=w=270:h=680:x='{xexpr}':y=540,boxblur=24:3[bl];[o][bl]overlay=x='{xexpr}':y=540{en}"
def run(src,out,extra="",ss=None,to=None):
    cut=(["-ss",str(ss)] if ss is not None else [])+(["-to",str(to)] if to is not None else [])
    subprocess.run(["ffmpeg","-loglevel","error","-y"]+cut+["-i",src,"-filter_complex",f"[0:v]fps=60,{PRE},{TM},{FIT}{extra}[v]","-map","[v]","-map","0:a",
      "-c:v","libx264","-crf","15","-preset","fast","-pix_fmt","yuv420p","-c:a","aac","-b:a","256k",out],check=True)
for n in ["k00","k01","k02","k03","k06","k07"]: run(f"raw/{n}.mov",f"b/{n}.mp4")
run("raw/k04.mov","b/k04.mp4",blur("if(lt(t,2.0),850,if(lt(t,2.5),850-(t-2.0)*440,max(500,630-(t-2.5)*260)))"))
run("raw/k05.mov","b/k05a.mp4",blur("370"),to=1.36)
run("raw/k05.mov","b/k05b.mp4",ss=1.37)
print("ok")
