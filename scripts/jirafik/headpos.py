import sys, subprocess, numpy as np, json
src=sys.argv[1]; times=json.loads(sys.argv[2])
out={}
for t in times:
    raw=subprocess.run(["ffmpeg","-loglevel","error","-c:v","libvpx-vp9","-ss",str(t),"-i",src,"-frames:v","1","-f","rawvideo","-pix_fmt","rgba","-"],capture_output=True).stdout
    a=np.frombuffer(raw,np.uint8).reshape(1920,1080,4)[:,:,3]
    rows=np.where((a[:,300:780]>128).sum(1)>20)[0]
    top=int(rows[0]) if len(rows) else 700
    cols=np.where(a[top:top+150,:]>128)[1]
    out[str(t)]={"headTop":top,"cx":int(cols.mean()) if len(cols) else 540}
print(json.dumps(out))
