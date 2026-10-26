import subprocess
TM="zscale=tin=arib-std-b67:pin=bt2020:min=bt2020nc:t=linear:npl=150,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=contrast=1.07:saturation=1.08:gamma=1.04,colorchannelmixer=rr=0.99:bb=1.03,unsharp=5:5:0.55"
PRE="scale=1080:1920:force_original_aspect_ratio=increase:force_divisible_by=2:flags=bicubic"
FIT="scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1"
subprocess.run(["ffmpeg","-loglevel","error","-y","-i","raw/full.mov","-filter_complex",f"[0:v]fps=60,{PRE},{TM},{FIT}[v]","-map","[v]","-map","0:a",
  "-c:v","libx264","-crf","14","-preset","fast","-pix_fmt","yuv420p","-c:a","aac","-b:a","256k","b/full60.mp4"],check=True)
print("ok")
