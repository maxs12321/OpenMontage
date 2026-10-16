import sys, subprocess, numpy as np, onnxruntime as ort, time
src, out = sys.argv[1], sys.argv[2]
W,H=1080,1920
sess=ort.InferenceSession("/home/user/models/rvm/rvm_mobilenetv3_fp32.onnx", providers=["CPUExecutionProvider"])
rec=[np.zeros([1,1,1,1],np.float32)]*4; ds=np.array([0.25],np.float32)
rd=subprocess.Popen(["ffmpeg","-loglevel","error","-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
wr=subprocess.Popen(["ffmpeg","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r","30","-i","-",
  "-c:v","libvpx-vp9","-pix_fmt","yuva420p","-b:v","0","-crf","28","-deadline","realtime","-cpu-used","8","-row-mt","1","-auto-alt-ref","0",out],stdin=subprocess.PIPE)
n=0; t0=time.time()
while True:
    buf=rd.stdout.read(W*H*3)
    if len(buf)<W*H*3: break
    fr=np.frombuffer(buf,np.uint8).reshape(H,W,3)
    x=(fr.astype(np.float32)/255).transpose(2,0,1)[None]
    fgr,pha,*rec=sess.run(None,{"src":x,"r1i":rec[0],"r2i":rec[1],"r3i":rec[2],"r4i":rec[3],"downsample_ratio":ds})
    a=(np.clip(pha[0,0],0,1)*255).astype(np.uint8)
    wr.stdin.write(np.dstack([fr,a]).tobytes()); n+=1
    if n%300==0: print(n, round(time.time()-t0,1), flush=True)
wr.stdin.close(); wr.wait(); print("frames",n)
