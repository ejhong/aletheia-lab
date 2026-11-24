# Final tally of DOI checks (Crossref + doi.org + DataCite for the one DataCite DOI)
import csv, json, sys, os
rows=list(csv.DictReader(open(sys.argv[1])))
raw=sys.argv[2]
final=[]
for r in rows:
    v=r['verdict']
    if v.startswith('DOI not found'):
        rec=json.load(open(os.path.join(raw,f"ref{r['ref']}.json")))
        code=json.loads(rec['handle_body']).get('responseCode')
        if code==100: v='DOI does not exist (doi.org)'
        else:
            dc=json.load(open(os.path.join(raw,'datacite_ref163.json')))['data']['attributes']
            v='DIFFERENT WORK (DataCite: %s)'%dc['titles'][0]['title']
    final.append((r['ref'],r['doi'],v,r['ref_author'],r['ref_year'],r['ref_title'],r['cr_author'],r['cr_title']))
from collections import Counter
c=Counter('different' if 'DIFFERENT' in f[2] else ('nonexistent' if 'not exist' in f[2] else f[2]) for f in final)
print("DOIs checked:",len(final)); print(c)
print("failing total:",c['different']+c['nonexistent'])
with open(sys.argv[3],'w',newline='') as fh:
    w=csv.writer(fh); w.writerow(['ref','doi','final_verdict','ref_first_author','ref_year','ref_title','crossref_first_author','crossref_title']); w.writerows(final)
for f in final:
    if f[2]!='match': print(f"| {f[0]} | {f[1]} | {f[2]} | {f[3]} {f[4]}: {f[5][:80]} | {f[6]}: {f[7][:80]} |")
