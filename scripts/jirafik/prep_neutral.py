# neutral HDR->SDR only (no sharpen/contrast/saturation), near-lossless 1440x2560 60 fps intermediate
import subprocess
TM="zscale=tin=arib-std-b67:pin=bt2020:min=bt2020nc:t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,zscale=t=bt709:m=bt709:r=tv:d=error_diffusion,format=yuv420p"
subprocess.run(["ffmpeg","-loglevel","error","-y","-i","raw/src.mov","-filter_complex",f"[0:v]fps=60,scale=1440:2560:flags=lanczos,{TM}[v]","-map","[v]","-map","0:a",
  "-c:v","libx264","-crf","8","-preset","fast","-pix_fmt","yuv420p","-c:a","aac","-b:a","320k","b/full60n.mp4"],check=True)
print("ok")
