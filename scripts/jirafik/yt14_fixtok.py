import json, re
T=json.load(open("b/tokens.json")); G=[w for w in json.load(open("b/full_g.json")) if w["word"].strip()]
def norm(s): return re.sub(r"[^\wё]","",s.lower().replace("ё","е"))
# whisper cuts the last word of a segment ("рас", "пар", "друг"): take GigaAM's full word at the same time
gi=0
for t in T:
    while gi<len(G)-1 and G[gi]["end"]<t["start"]-0.05: gi+=1
    for g in G[max(0,gi-1):gi+3]:
        a,b=norm(t["text"]),norm(g["word"])
        if a and b!=a and b.startswith(a) and len(b)>len(a)+1 and abs(g["start"]-t["start"])<0.3:
            tail=re.sub(r"^.*?([.,!?…:;]*)$",r"\1",t["text"])
            t["text"]=(g["word"].strip()[:1].upper()+g["word"].strip()[1:] if t["text"][:1].isupper() else g["word"].strip())+tail; break
FIX={"Ирко":"РКО","Аркавр":"РКО","RQ.":"РКО.","IP":"ИП","PSB":"ПСБ","ННПД":"НПД","ПННПД":"ИП на НПД","Walburys,":"Wildberries,","Ozone,":"Ozon,",
     "дефамина":"дофамина","халда":"холда","CD":"ЦД","Кота":"У кого-то","ФСЗ":"ФЗ","Мфц,":"МФЦ,","оферы":"офферы","оферов,":"офферов,","Озонбанк":"Озон Банк",
     "заофер":"оффер","колд":"холд"}
for i,t in enumerate(T):
    w=t["text"]; k=w.rstrip(".,!?…:;"); tail=w[len(k):]
    if k in FIX: t["text"]=FIX[k]+tail
    elif w in FIX: t["text"]=FIX[w]
    if norm(t["text"])=="и" and i+1<len(T) and T[i+1]["text"].startswith("ИП на НПД"): t["text"]=""
# "за заофер" -> "холд за оффер"
for i in range(len(T)-1):
    if norm(T[i]["text"])=="за" and T[i+1]["text"].startswith("оффер") and i>0 and norm(T[i-1]["text"])=="что": T[i]["text"]="холд за"
T=[t for t in T if t["text"]]
json.dump(T,open("b/tokens_fixed.json","w"),ensure_ascii=False,indent=0)
open("b/text_fixed.txt","w").write(" ".join(t["text"] for t in T)); print(len(T))
