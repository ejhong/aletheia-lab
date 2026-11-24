import json,sys
a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2]))
mx={}
def walk(x,y,p):
    if isinstance(x,dict):
        for k in x: walk(x[k],y[k],p+'/'+k)
    elif isinstance(x,list):
        for i,(u,v) in enumerate(zip(x,y)): walk(u,v,p+'[]')
    elif isinstance(x,(int,float)) and isinstance(y,(int,float)) and not isinstance(x,bool):
        key=p.split('/')[-1]
        d=abs(x-y)/max(1e-12,abs(x)) if x else abs(y)
        mx[key]=max(mx.get(key,0),d)
    elif x!=y: print('DIFF',p,x,y)
walk(a,b,'')
for k,v in sorted(mx.items(),key=lambda t:-t[1]):
    if v>0: print(f'{k:35s} max rel diff {v:.2e}')
