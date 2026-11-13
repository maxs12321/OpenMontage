# word fixes for this video's subtitles (index -> text, "" drops the word)
import json
T=json.load(open("b/tokens_fixed.json"))
F={52:"В первом",56:"РКО",103:"нише РКО",105:"год.",106:"В",107:"команде",108:"отвечаю",110:"трафик",112:"техническую часть:",113:"как подаются",
   151:"те,",267:"Не",315:"бесплатно",406:"Т-Банке.",499:"на НПД",510:"4–6 %.",538:"ИП",539:"на",540:"НПД",637:"",717:"В",
   823:"первые",826:"Окружение:",827:"бесплатно",828:"даёт",843:"холодные",952:"Telegram-канале."}
for i,v in F.items(): T[i]["text"]=v
for t in T: t["text"]=t["text"].replace("RKO","РКО")
T=[t for t in T if t["text"]]
json.dump(T,open("b/tokens_final.json","w"),ensure_ascii=False,indent=0)
print(" ".join(t["text"] for t in T[45:120]))
