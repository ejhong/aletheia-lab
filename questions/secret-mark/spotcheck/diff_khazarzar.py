import sys,re,json,unicodedata,difflib
import unicodedata as U; t=U.normalize("NFC",open(sys.argv[1]).read())
i=t.index('Транслитерация'); s=t[i:]
j=s.index(U.normalize('NFC','ἐξήγησις')); s=s[:j+len('ἐξήγησις')]
s=s[s.index('1.'):]
s=re.sub(r'-\s+','',s)           # join hyphenated line breaks
s=re.sub(r'\b(I|II|III)\b',' ',s)
def norm(x):
    x=unicodedata.normalize('NFD',x.lower()); x=''.join(c for c in x if unicodedata.category(c)!='Mn'); return x.replace('ς','σ')
kh=re.findall(r'[α-ω]+',norm(s))
L=json.load(open(sys.argv[2]))
st=L['heading']+L['full_no_heading']
print('khazarzar tokens',len(kh),'study tokens',len(st))
sm=difflib.SequenceMatcher(a=kh,b=st,autojunk=False)
for op,a0,a1,b0,b1 in sm.get_opcodes():
    if op!='equal': print(op,'KH:',' '.join(kh[a0:a1]),'| STUDY:',' '.join(st[b0:b1]),'| ctx:',' '.join(st[max(0,b0-3):b0]))
