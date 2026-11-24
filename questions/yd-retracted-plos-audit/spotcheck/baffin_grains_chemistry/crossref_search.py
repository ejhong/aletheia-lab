# For DOIs that do not exist, search Crossref by the reference's title to find the registered DOI (to confirm the cited DOI is wrong, not a query artefact)
import csv, json, sys, time, urllib.request, urllib.parse, os
refs={r['label']:r for r in json.load(open(sys.argv[1]))}
rows=[r for r in csv.DictReader(open(sys.argv[2])) if 'not exist' in r['final_verdict']]
for r in rows:
    o=refs[r['ref']]; q=(o['title'] or o['text'])[:200]+' '+(o['first_author'] or '')
    url='https://api.crossref.org/works?rows=1&query.bibliographic='+urllib.parse.quote(q)
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'generic-reference-checker/1.0'}),timeout=30) as resp: body=json.loads(resp.read())
    except Exception as e: body={'error':repr(e)}
    json.dump({'ref':r['ref'],'query':q,'url':url,'body':body},open(os.path.join(sys.argv[3],f"ref{r['ref']}.json"),'w'))
    it=(body.get('message',{}).get('items') or [{}])[0]
    print(f"[{r['ref']}] cited {r['doi']} -> top hit {it.get('DOI')} | {(it.get('title') or [''])[0][:90]} | score {it.get('score')}")
    time.sleep(0.7)
