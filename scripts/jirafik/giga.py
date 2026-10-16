import sys, json, wave, numpy as np, sherpa_onnx
wav,out=sys.argv[1],sys.argv[2]
D="/home/user/models/sherpa-onnx-nemo-transducer-giga-am-v2-russian-2025-04-19/"
rec=sherpa_onnx.OfflineRecognizer.from_transducer(encoder=D+"encoder.int8.onnx",decoder=D+"decoder.onnx",joiner=D+"joiner.onnx",tokens=D+"tokens.txt",model_type="nemo_transducer",num_threads=4)
with wave.open(wav) as w: a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
# chunk by VAD-ish fixed segments from whisper pass to keep model inputs short
segs=json.load(open(sys.argv[3]))
words=[]
for sg in segs:
    st=max(0,sg["start"]-0.15); en=sg["end"]+0.15
    s=rec.create_stream(); s.accept_waveform(16000,a[int(st*16000):int(en*16000)]); rec.decode_stream(s)
    r=s.result; toks=r.tokens; ts=list(r.timestamps)
    print(f"[{st:.2f}] {r.text}")
    cur=None
    for t,tm in zip(toks,ts):
        tm+=st
        if t.startswith("▁") or t==" " or cur is None:
            if cur and cur["word"]: words.append(cur)
            cur={"word":t.replace("▁",""),"start":tm,"end":tm+0.08}
        else:
            cur["word"]+=t; cur["end"]=tm+0.08
    if cur and cur["word"]: words.append(cur)
json.dump(words,open(out,"w"),ensure_ascii=False,indent=0)
print(" ".join(f'{w["word"]}@{w["start"]:.2f}' for w in words))
