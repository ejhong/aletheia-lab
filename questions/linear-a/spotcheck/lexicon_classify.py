"""Classify the study's 188 'mismatches' (Test 5) as standard Semitic morphology vs real conflicts with the stated classes."""
import json,sys,itertools,collections,pathlib
rows=json.load(open(sys.argv[1]))
PRE=set("MTYNSW"); SUF=set("TNMYW")
def root_variants(r):
    out={r}
    # weak radicals W/Y may be unwritten (assimilated / vocalised)
    idx=[i for i,c in enumerate(r) if c in "WY"]
    for k in range(1,len(idx)+1):
        for comb in itertools.combinations(idx,k):
            out.add("".join(c for i,c in enumerate(r) if i not in comb))
    # geminate C2=C3 written once
    for v in list(out):
        if len(v)>=2 and v[-1]==v[-2]: out.add(v[:-1])
    # reduplication of a biradical (C1C2C1C2) is also a standard pattern
    for v in list(out):
        if len(v)==2: out.add(v+v)
    return {v for v in out if v}
def explain(word,root):
    if word==root: return "exact"
    rv=root_variants(root)
    if word in rv: return "weak radical / geminate"
    for v in rv:
        for a in range(0,3):
            for b in range(0,3):
                if a+b==0 or a+b+len(v)!=len(word): continue
                if word[a:len(word)-b if b else None]==v and all(c in PRE for c in word[:a]) and all(c in SUF for c in word[len(word)-b:]):
                    return "affix(es) from standard Semitic set" + (" + weak/geminate" if v!=root else "")
    if sorted(word)==sorted(root): return "metathesis"
    if root in word: return "root inside word, non-standard extra consonants"
    if len(word)<len(root): return "word lacks a strong radical"
    return "class conflict / other"
C=collections.Counter(); ex=collections.defaultdict(list)
for r in rows:
    if r['match_clean']: k="exact (after dropping glosses)"
    else: k=explain(r['sk9'],r['root_sk_clean'])
    C[k]+=1; ex[k].append(f"{r['word']} [{r['root'][:40]}] {r['sk9']} vs {r['root_sk_clean']}")
n=len(rows)
for k,v in C.most_common(): print(f"{v:4d} {v/n:6.1%}  {k}  e.g. {ex[k][:3]}")
