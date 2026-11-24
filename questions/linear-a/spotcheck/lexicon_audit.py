"""Re-examine the study's Test 5 lexicon-fidelity numbers (42.2% etc.) entry by entry."""
import json,sys,importlib.util,pathlib,re,random,collections
W=pathlib.Path(sys.argv[1]); OUT=pathlib.Path(sys.argv[2])
spec=importlib.util.spec_from_file_location("rla",W/"analysis/run_linear_a.py"); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
K=W/"data/kaphtor/data"
sv=json.load(open(K/"linear-a/sign_values.json")); sm,lbm,nov=m.load_sign_table(sv)
E=json.load(open(K/"linear-a/lexicon.json"))["entries"]
rows=[]
for e in E:
    w=(e.get("word") or "").strip().upper().replace("₂","2").replace("₃","3").replace("₄","4")
    parts=[p for p in w.split("-") if p]
    r=e.get("root") or ""
    if len(parts)>=3 and r and "+" not in r and "+" not in w:
        sk9,ok=m.linear_a_word_to_skeleton(w,sm,False)
        rk9=m.project_phoneme_string(r,False)
        if ok and len(sk9)>=2 and len(rk9)>=2:
            # cleaner root parse: drop quoted glosses and parenthetical comments, take text before first quote/paren/semicolon
            r_clean=re.split(r'["“(;,/]| or | ~ ',r)[0]
            rk_clean=m.project_phoneme_string(r_clean,False)
            ps=str(e.get("proto_semitic"))[:80]
            rows.append(dict(word=w,root=r,ps=ps,tier=e.get("confidence"),sk9=sk9,root_sk_study=rk9,root_sk_clean=rk_clean,
                             match_study=sk9==rk9,match_clean=sk9==rk_clean,has_quote=('"' in r or '“' in r),has_paren='(' in r))
n=len(rows); print("evaluated",n)
print("study strict match",sum(r['match_study'] for r in rows), f"{sum(r['match_study'] for r in rows)/n:.4f}")
print("root strings with a quoted gloss",sum(r['has_quote'] for r in rows), "with parenthesis",sum(r['has_paren'] for r in rows))
print("match after dropping quoted gloss/comments",sum(r['match_clean'] for r in rows), f"{sum(r['match_clean'] for r in rows)/n:.4f}")
mis=[r for r in rows if not r['match_study']]
print("study mismatches",len(mis), "of which fixed by clean parse",sum(r['match_clean'] for r in mis))
# remaining mismatches: classify
rem=[r for r in mis if not r['match_clean']]
def cls(r):
    a,b=r['sk9'],r['root_sk_clean']
    if len(a)>len(b) and (a.startswith(b) or a.endswith(b) or b in a): return "word = root + affix consonant(s)"
    if len(a)<len(b): return "word shorter than root (radical unwritten)"
    if sorted(a)==sorted(b): return "same consonants, different order"
    return "other"
print(collections.Counter(cls(r) for r in rem))
random.seed(7)
sample=random.sample(mis,10)
with open(OUT/"lexicon_audit_sample.tsv","w") as f:
    f.write("word\ttier\troot (as filed)\tword_skel\troot_skel_study\troot_skel_clean\tmatch_clean\n")
    for r in sample: f.write(f"{r['word']}\t{r['tier']}\t{r['root']}\t{r['sk9']}\t{r['root_sk_study']}\t{r['root_sk_clean']}\t{r['match_clean']}\n")
for r in sample: print(r['word'],'|',r['tier'],'|',r['root'][:90],'| word',r['sk9'],'| study root',r['root_sk_study'],'| clean root',r['root_sk_clean'])
json.dump(rows,open(OUT/"lexicon_audit_rows.json","w"),ensure_ascii=False,indent=1)
