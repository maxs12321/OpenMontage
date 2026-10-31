# final audio = cut voice (b/cut_n.mp4) + SFX at their props times (Remotion's own audio lags ~42 ms, so mix here)
import json, subprocess
P=json.load(open("/home/user/OpenMontage/remotion-composer/public/demo-props/jirafik-iphone11.json"))
pub="/home/user/OpenMontage/remotion-composer/public/"
ins=["-i","b/cut_n.mp4"]; fl=[]; lab=["[0:a]"]
for k,s in enumerate(P["sfx"]):
    ins+=["-i",pub+s["src"]]; ms=int(s["at"]*1000)
    fl.append(f"[{k+1}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={s['volume']},adelay={ms}|{ms}[s{k}]"); lab.append(f"[s{k}]")
fl.append("".join(lab)+f"amix=inputs={len(lab)}:normalize=0:duration=first,atrim=0:{P['videoDuration']}[a]")
subprocess.run(["ffmpeg","-loglevel","error","-y"]+ins+["-filter_complex",";".join(fl),"-map","[a]","-ar","48000","-c:a","pcm_s16le","b/final_audio_n.wav"],check=True)
print("ok")
