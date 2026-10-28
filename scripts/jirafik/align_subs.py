# subtitle tokens: GigaAM word timings + Whisper punctuation/digits, aligned with difflib
import json, re, difflib
g=[w for w in json.load(open("b/full_g.json")) if w["word"].strip()]
ws=json.load(open("b/full_w.json"))
def norm(s): return re.sub(r"[^\wё]","",s.lower().replace("ё","е"))
W=[]
for s in ws:
    toks=s["text"].split()
    for t in toks: W.append(t)
a=[norm(w["word"]) for w in g]; b=[norm(t) for t in W]
sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
out=[]
for op,i1,i2,j1,j2 in sm.get_opcodes():
    if op=="equal":
        for k in range(i2-i1):
            out.append({"text":W[j1+k],"start":g[i1+k]["start"],"end":g[i1+k]["end"]})
    elif op=="replace" and (i2-i1)==(j2-j1):
        # same count: whisper often truncates the last word of a segment ("мяг", "обслуж") — trust giga's word then,
        # but keep whisper's digits, capitals and punctuation
        for k in range(i2-i1):
            gw=g[i1+k]["word"].strip(); wt=W[j1+k]
            if re.search(r"\d",wt) or difflib.SequenceMatcher(None,norm(gw),norm(wt)).ratio()<0.5: txt=wt
            else:
                tail=re.sub(r"^.*?([.,!?…:;]*)$",r"\1",wt)
                txt=(gw[:1].upper()+gw[1:] if wt[:1].isupper() else gw)+tail
            out.append({"text":txt,"start":g[i1+k]["start"],"end":g[i1+k]["end"],"rep":True})
    elif op=="replace":
        # whisper tokens spread over the giga words' time span
        t0=g[i1]["start"]; t1=g[i2-1]["end"]; n=j2-j1
        for k in range(n):
            out.append({"text":W[j1+k],"start":t0+(t1-t0)*k/n,"end":t0+(t1-t0)*(k+1)/n,"rep":True})
    elif op=="delete":   # words whisper missed (its segments are often cut short)
        for k in range(i1,i2):
            out.append({"text":g[k]["word"].strip(),"start":g[k]["start"],"end":g[k]["end"],"giga":True})
json.dump(out,open("b/tokens.json","w"),ensure_ascii=False,indent=0)
print(len(g),len(W),len(out))
open("b/text.txt","w").write(" ".join(t["text"] for t in out))
