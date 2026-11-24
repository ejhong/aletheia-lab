# Measure SEM scale bar and dark pore spots in SI Fig S30 SEM panel (embedded image si-000.png)
import sys
from PIL import Image
import numpy as np
from scipy import ndimage
im=np.array(Image.open(sys.argv[1]).convert('L')).astype(int)
# scale bar: search rows 480-500, x 440-600, bright run
best=None
for y in range(478,500):
    row=im[y,440:600]
    xs=np.where(row>200)[0]
    if len(xs)>40:
        # longest contiguous run
        runs=np.split(xs,np.where(np.diff(xs)!=1)[0]+1)
        r=max(runs,key=len)
        if best is None or len(r)>best[1]: best=(y,len(r),440+r[0],440+r[-1])
print("scale bar row, length px, x0, x1:",best)
pxum=best[1]/20.0
print("px per um: %.2f"%pxum)
# pores: dark local minima in porous wall area (crop around upper chamber)
y0,y1,x0,x1=[int(v) for v in sys.argv[2:6]]
sub=im[y0:y1,x0:x1].astype(float)
bg=ndimage.median_filter(sub,size=9)
d=bg-sub
mask=d>25
lab,n=ndimage.label(mask)
sizes=ndimage.sum(mask,lab,range(1,n+1))
sizes=sizes[(sizes>=1)&(sizes<60)]
eqd=2*np.sqrt(sizes/np.pi)/pxum
print("n dark spots",len(sizes)," equiv diameter um: median %.2f, p10 %.2f, p90 %.2f"%(np.median(eqd),np.percentile(eqd,10),np.percentile(eqd,90)))
# centre spacing
cent=ndimage.center_of_mass(mask,lab,range(1,n+1))
cent=np.array(cent)
from scipy.spatial import cKDTree
t=cKDTree(cent); dd,_=t.query(cent,k=2)
print("nearest-neighbour spacing um: median %.2f"%(np.median(dd[:,1])/pxum))
