import subprocess
R="raw2/"
P=[("a",0.0,6.454),("b",0.342,None),("c",0.178,None),("d",0.598,None),("e",0.134,None),("f",0.008,None)]
ends=[6.454,12.630,18.691,24.287,28.443,32.715]
starts=[0.0]+ends[:-1]
TM="zscale=tin=arib-std-b67:pin=bt2020:min=bt2020nc:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,curves=all='0/0 0.5/0.56 1/1',colorchannelmixer=rr=0.98:gg=0.99:bb=1.09,eq=saturation=0.95"
args=["ffmpeg","-loglevel","error","-y"]; fc=[]
for i,(p,off,_) in enumerate(P):
    args+=["-i",R+f"part_{p}.mov"]
    dur=ends[i]-starts[i]
    fc.append(f"[{i}:v]trim=start={off}:duration={dur:.3f},setpts=PTS-STARTPTS,fps=30,{TM},scale=1080:1920:flags=lanczos,setsar=1[v{i}]")
args+=["-i","raw/source.mov"]
fc.append("".join(f"[v{i}]" for i in range(len(P)))+f"concat=n={len(P)}:v=1:a=0[vo]")
args+=["-filter_complex",";".join(fc),"-map","[vo]","-map",f"{len(P)}:a","-c:v","libx264","-crf","12","-preset","slow","-pix_fmt","yuv420p","-c:a","copy","-shortest","raw/master_hq.mp4"]
subprocess.run(args,check=True)
