# Compare Crossref-registered metadata with each reference's stated title / first author / year
import sys, json, os, re, unicodedata, difflib, csv
refs=json.load(open(sys.argv[1])); raw=sys.argv[2]
def norm(s):
    s=unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower()
    s=re.sub(r'<[^>]+>','',s); s=re.sub(r'[^a-z0-9 ]+',' ',s); return re.sub(r'\s+',' ',s).strip()
rows=[]
for o in refs:
    if not o['doi']: continue
    rec=json.load(open(os.path.join(raw,o['id']+'.json')))
    st=rec.get('status')
    r=dict(ref=o['label'],id=o['id'],doi=o['doi'],status=st,ref_title=o['title'] or '',ref_author=o['first_author'] or '',ref_year=o['year'] or '',cr_title='',cr_author='',cr_year='',title_sim=None,verdict='')
    if st==200:
        m=rec['body']['message']
        r['cr_title']=(m.get('title') or [''])[0]
        au=m.get('author') or []
        r['cr_author']=(au[0].get('family') or au[0].get('name') or '') if au else ''
        dp=(m.get('published-print') or m.get('published-online') or m.get('issued') or {}).get('date-parts',[[None]])
        yrs=set()
        for k in ('issued','published-print','published-online','created'):
            v=m.get(k,{}).get('date-parts',[[None]])[0][0]
            if v: yrs.add(str(v))
        r['cr_year']='/'.join(sorted(yrs))
        rt=norm(r['ref_title']); ct=norm(r['cr_title'])
        if not rt:  # no article-title (book etc): compare against whole ref text
            rt=norm(o['text'])
            sim = 1.0 if ct and ct in rt else difflib.SequenceMatcher(None,ct,rt).ratio()
        else:
            sim=difflib.SequenceMatcher(None,rt,ct).ratio()
            if ct and (ct in rt or rt in ct) and min(len(ct),len(rt))>15: sim=max(sim,0.95)
        r['title_sim']=round(sim,3)
        a_ok = norm(r['ref_author']) and norm(r['cr_author']) and (norm(r['ref_author'])==norm(r['cr_author']) or norm(r['ref_author']) in norm(r['cr_author']) or norm(r['cr_author']) in norm(r['ref_author']))
        r['author_match']=bool(a_ok)
        r['year_match']= r['ref_year'] in yrs if r['ref_year'] else None
        if sim>=0.8: r['verdict']='match'
        elif sim>=0.5 and a_ok: r['verdict']='partial (check)'
        else: r['verdict']='DIFFERENT WORK' if not a_ok else 'title differs, author matches (check)'
    else:
        r['verdict']='DOI not found' if st==404 else f'lookup failed ({st})'
    rows.append(r)
with open(sys.argv[3],'w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())+[k for k in ('author_match','year_match') if k not in rows[0]]); w.writeheader(); w.writerows(rows)
from collections import Counter
print(Counter(r['verdict'] for r in rows))
for r in rows:
    if r['verdict']!='match':
        print(f"[{r['ref']}] {r['doi']} | {r['verdict']} sim={r['title_sim']} | REF: {r['ref_author']} {r['ref_year']} '{r['ref_title'][:90]}' | CROSSREF: {r['cr_author']} {r['cr_year']} '{r['cr_title'][:90]}'")
