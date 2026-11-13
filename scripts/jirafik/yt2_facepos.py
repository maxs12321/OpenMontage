# where the speaker sits at given source times: x-centre (0..1) of the person matte's upper half
import sys, json, subprocess, numpy as np, onnxruntime as ort
src=sys.argv[1]; ts=json.loads(sys.argv[2])
sess=ort.InferenceSession("/home/user/models/rvm/rvm_mobilenetv3_fp32.onnx", providers=["CPUExecutionProvider"])
W,H=512,288; out={}
for t in ts:
    raw=subprocess.run(["ffmpeg","-loglevel","error","-ss",str(t),"-i",src,"-frames:v","1","-vf",f"scale={W}:{H}","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    fr=np.frombuffer(raw,np.uint8).reshape(H,W,3).astype(np.float32)/255
    rec=[np.zeros([1,1,1,1],np.float32)]*4
    for _ in range(3):   # a few passes on the same frame let the recurrent state settle
        fgr,pha,*rec=sess.run(None,{"src":fr.transpose(2,0,1)[None],"r1i":rec[0],"r2i":rec[1],"r3i":rec[2],"r4i":rec[3],"downsample_ratio":np.array([0.5],np.float32)})
    a=pha[0,0][:H//2]; col=a.sum(0); x=float((col*np.arange(W)).sum()/max(col.sum(),1e-6))/W
    out[str(t)]=round(x,3)
print(json.dumps(out))
