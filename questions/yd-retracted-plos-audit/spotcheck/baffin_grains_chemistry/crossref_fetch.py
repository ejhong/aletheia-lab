# Look up each reference DOI on the public Crossref REST API; save raw JSON responses. Generic UA, no contact details.
import sys, json, time, urllib.request, urllib.parse, urllib.error, os, hashlib
refs=json.load(open(sys.argv[1])); outdir=sys.argv[2]
UA='generic-reference-checker/1.0'
done=0
for o in refs:
    d=o['doi']
    if not d: continue
    fn=os.path.join(outdir, o['id']+'.json')
    if os.path.exists(fn): continue
    url='https://api.crossref.org/works/'+urllib.parse.quote(d, safe='/')
    req=urllib.request.Request(url, headers={'User-Agent':UA})
    rec={'ref_id':o['id'],'doi':d,'url':url,'retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            rec['status']=resp.status; rec['body']=json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        rec['status']=e.code; rec['body']=e.read().decode('utf-8','replace')[:500]
    except Exception as e:
        rec['status']=None; rec['error']=repr(e)
    json.dump(rec,open(fn,'w'),ensure_ascii=False)
    done+=1
    time.sleep(0.6)
print("fetched",done)
