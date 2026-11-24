# For DOIs Crossref did not find: ask the DOI handle system whether they exist, and which registration agency holds them.
import sys, json, csv, time, urllib.request, urllib.parse, os
rows=[r for r in csv.DictReader(open(sys.argv[1])) if r['verdict'].startswith('DOI not found')]
UA='generic-reference-checker/1.0'
def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':UA}),timeout=30) as r: return r.status, r.read().decode('utf-8','replace')
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf-8','replace')
    except Exception as e: return None, repr(e)
out=[]
for r in rows:
    d=r['doi']; q=urllib.parse.quote(d,safe='/')
    s1,b1=get('https://doi.org/api/handles/'+q); time.sleep(0.5)
    s2,b2=get('https://doi.org/doiRA/'+q); time.sleep(0.5)
    rec=dict(ref=r['ref'],doi=d,handle_status=s1,handle_body=b1[:2000],ra_status=s2,ra_body=b2[:500],retrieved_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
    json.dump(rec,open(os.path.join(sys.argv[2],f"ref{r['ref']}.json"),'w'))
    try: code=json.loads(b1).get('responseCode')
    except Exception: code=None
    try: ra=json.loads(b2)[0].get('RA') or json.loads(b2)[0].get('status')
    except Exception: ra=b2[:80]
    url=''
    try:
        for v in json.loads(b1).get('values',[]):
            if v.get('type')=='URL': url=v['data']['value']
    except Exception: pass
    print(f"[{r['ref']}] {d}: handle responseCode={code} (1=exists,100=not found) RA={ra} URL={url}")
