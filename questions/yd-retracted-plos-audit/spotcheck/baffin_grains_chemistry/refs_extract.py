# Extract reference list (id, text, DOI, year, first author surname, title guess) from JATS XML -> JSON
import sys, re, json
import xml.etree.ElementTree as ET
r=ET.parse(sys.argv[1]).getroot()
out=[]
for ref in r.iter('ref'):
    rid=ref.attrib.get('id'); lab=ref.find('label')
    mc=ref.find('.//mixed-citation') or ref.find('.//element-citation')
    txt=re.sub(r'\s+',' ',''.join(mc.itertext()) if mc is not None else ''.join(ref.itertext())).strip()
    doi_el=ref.find(".//pub-id[@pub-id-type='doi']")
    doi=(doi_el.text or '').strip() if doi_el is not None else ''
    src='pub-id' if doi else ''
    if not doi:
        m=re.search(r'10\.\d{4,9}/[^\s]+',txt)
        if m: doi=m.group(0).rstrip('.,;'); src='text'
    yr=ref.find('.//year'); title=ref.find('.//article-title'); sname=ref.find('.//name/surname')
    out.append(dict(id=rid,label=lab.text if lab is not None else None,text=txt,doi=doi,doi_src=src,
        year=(yr.text if yr is not None else None),title=(re.sub(r'\s+',' ',''.join(title.itertext())).strip() if title is not None else None),
        first_author=(sname.text if sname is not None else None),source=(lambda s: s.text if s is not None else None)(ref.find('.//source'))))
json.dump(out,open(sys.argv[2],'w'),indent=1,ensure_ascii=False)
print(len(out),"refs;",sum(1 for o in out if o['doi']),"with DOI;",sum(1 for o in out if o['doi_src']=='text'),"DOI only in text;",sum(1 for o in out if o['title']),"with article-title")
from collections import Counter
c=Counter(o['doi'].lower() for o in out if o['doi']); print("duplicate DOIs:",{k:v for k,v in c.items() if v>1})
