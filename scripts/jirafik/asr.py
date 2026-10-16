import sys, json, wave, numpy as np, sherpa_onnx
wav, out = sys.argv[1], sys.argv[2]
M="/home/user/models/"; D=M+"sherpa-onnx-whisper-turbo/"
with wave.open(wav) as w: a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
sr=16000
cfg=sherpa_onnx.VadModelConfig(); cfg.silero_vad.model=M+"silero_vad.onnx"; cfg.silero_vad.min_silence_duration=float(sys.argv[3]) if len(sys.argv)>3 else 0.35; cfg.silero_vad.min_speech_duration=0.2; cfg.silero_vad.threshold=0.4; cfg.sample_rate=sr
vad=sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=60)
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=D+"turbo-encoder.int8.onnx", decoder=D+"turbo-decoder.int8.onnx", tokens=D+"turbo-tokens.txt", language="ru", task="transcribe", num_threads=4)
segs=[]
ws=cfg.silero_vad.window_size
for i in range(0,len(a),ws):
    vad.accept_waveform(a[i:i+ws])
    while not vad.empty():
        s=vad.front; segs.append((s.start/sr, np.array(s.samples))); vad.pop()
vad.flush()
while not vad.empty():
    s=vad.front; segs.append((s.start/sr, np.array(s.samples))); vad.pop()
res=[]
for st,sm in segs:
    s=rec.create_stream(); s.accept_waveform(sr,sm); rec.decode_stream(s)
    t=s.result.text.strip(); en=st+len(sm)/sr
    print(f"[{st:6.2f}-{en:6.2f}] {t}")
    res.append({"start":round(st,2),"end":round(en,2),"text":t})
json.dump(res,open(out,"w"),ensure_ascii=False,indent=1)
