"""Check the Linear B control file, the held-out split and the 15.72 multiplicity figure."""
import json,sys,importlib.util,pathlib,re,collections,statistics
W=pathlib.Path(sys.argv[1])
spec=importlib.util.spec_from_file_location("rla",W/"analysis/run_linear_a.py"); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
K=W/"data/kaphtor/data"; D=W/"data"
txt=(D/"linearb_xyz_inscriptions.js").read_text(encoding="utf-8",errors="ignore")
print("LB file head:",txt[:600].replace("\n"," "))
# per-inscription site prefix
names=re.findall(r'"name"\s*:\s*"([^"]+)"',txt)
print("LB inscriptions with name field:",len(names), collections.Counter(n[:2] for n in names).most_common(8))
# words per site
site_words=collections.defaultdict(collections.Counter)
for mm in re.finditer(r'"name"\s*:\s*"([^"]+)".*?"transliteratedWords"\s*:\s*\[([^\]]*)\]',txt,flags=re.S):
    site=mm.group(1)[:2]
    for w in re.findall(r'"([^"]+)"',mm.group(2)):
        ws=w.strip()
        parts=ws.split("-")
        if len(parts)>=3 and all(re.fullmatch(r"[a-z]{1,3}[0-9₂₃₄]*",p) for p in parts):
            site_words[site][ws.lower()]+=1
lbc=m.extract_linear_b_words(D/"linearb_xyz_inscriptions.js")
kn=set(site_words.get("KN",{})); py=set(site_words.get("PY",{}))
print("LB clean types",len(lbc),"KN types",len(kn),"PY types",len(py),"KN-only",len(kn-py))
import random; random.seed(3); print("random LB words:",random.sample(sorted(lbc),30))
# known Greek words present?
for w in ["wa-na-ka","ko-no-so","pa-ka-na","e-re-u-te-ro","ti-ri-po-de","di-pa","a-mo-ra-ma","po-ti-ni-ja","te-o-jo","do-e-ro","ke-ra-me-u","ka-ke-we","e-ra-wo","i-je-re-ja","pa-i-to","a-ni-ja","wo-ko"]:
    print(w, w in lbc, end="; ")
print()
# held-out split
lex=json.load(open(K/"linear-a/lexicon.json"))["entries"]
lexw={(e.get("word") or "").strip().upper().replace("₂","2").replace("₃","3").replace("₄","4") for e in lex}
ono=json.load(open(K/"linear-a/onomasticon.json"))
ono_s=json.dumps(ono,ensure_ascii=False).upper().replace("₂","2").replace("₃","3")
tr=json.dumps(json.load(open(K/"linear-a/translations.json")),ensure_ascii=False).upper().replace("₂","2").replace("₃","3")
un=json.load(open(K/"linear-a/unread_words.json"))["entries"]
unw={(k if isinstance(un,dict) else (e.get("word") or "")).upper().replace("₂","2").replace("₃","3") for k,e in (un.items() if isinstance(un,dict) else enumerate(un))} if un else set()
if isinstance(un,list): unw={(e.get("word") or "").upper().replace("₂","2").replace("₃","3") for e in un}
lac=m.extract_linear_a_words(json.load(open(K/"linear-a/corpus.json")))
ho=[w for w in lac if w not in lexw]
in_ono=[w for w in ho if f'"{w}"' in ono_s]
in_tr=[w for w in ho if w in tr]
in_un=[w for w in ho if w in unw]
print("held-out",len(ho),"in onomasticon",len(in_ono),"mentioned in translations.json",len(in_tr),"in unread_words",len(in_un))
print("held-out examples in onomasticon:",in_ono[:10])
# multiplicity distribution behind 15.72
sem=json.load(open(K/"semitic-roots/semitic_roots.json"))
sf=[m.parse_semitic_ps_variants(r.get("ps","")) for r in sem["roots"]]
_,mult=m.build_root_skeletons(sf,False)
sv=json.load(open(K/"linear-a/sign_values.json")); sm,_,_=m.load_sign_table(sv)
vals=[];lens=[]
for e in lex:
    w=(e.get("word") or "").strip().upper().replace("₂","2").replace("₃","3").replace("₄","4")
    parts=[p for p in w.split("-") if p]; r=e.get("root") or ""
    if len(parts)>=3 and r and "+" not in r and "+" not in w:
        sk,ok=m.linear_a_word_to_skeleton(w,sm,False); rk=m.project_phoneme_string(r,False)
        if ok and len(sk)>=2 and len(rk)>=2:
            vals.append(mult.get(sk,0)); lens.append(len(sk))
print("multiplicity n",len(vals),"mean",round(statistics.mean(vals),2),"median",statistics.median(vals),"share zero",round(sum(v==0 for v in vals)/len(vals),3))
for L in (2,3,4):
    v=[x for x,l in zip(vals,lens) if (l==L if L<4 else l>=4)]
    print(" L",L,"n",len(v),"mean",round(statistics.mean(v),2) if v else None,"median",statistics.median(v) if v else None,"zero",sum(x==0 for x in v))
