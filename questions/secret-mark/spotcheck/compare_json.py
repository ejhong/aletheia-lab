import json,sys,math
a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2]))
diffs=[]
def walk(x,y,p):
    if isinstance(x,dict) and isinstance(y,dict):
        for k in set(x)|set(y):
            if k not in x or k not in y: diffs.append((p+'/'+str(k),'missing')); continue
            walk(x[k],y[k],p+'/'+str(k))
    elif isinstance(x,list) and isinstance(y,list):
        if len(x)!=len(y): diffs.append((p,'len %d vs %d'%(len(x),len(y)))); return
        for i,(u,v) in enumerate(zip(x,y)): walk(u,v,p+'[%d]'%i)
    elif isinstance(x,float) or isinstance(y,float):
        if not (isinstance(x,(int,float)) and isinstance(y,(int,float)) and (x==y or abs(x-y)<=1e-12*max(1,abs(x)))): diffs.append((p,x,y))
    elif x!=y: diffs.append((p,x,y))
walk(a,b,'')
print('n diffs',len(diffs))
for d in diffs[:50]: print(d)
