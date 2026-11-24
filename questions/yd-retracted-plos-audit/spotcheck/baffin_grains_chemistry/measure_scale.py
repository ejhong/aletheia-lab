import sys
from PIL import Image
import numpy as np
im=np.array(Image.open(sys.argv[1]).convert('L')).astype(int)
# find scale bar: bright horizontal run in bottom info strip
h,w=im.shape
for y in range(h-60,h):
    row=im[y]
    runs=[];start=None
    for x,v in enumerate(row):
        if v>200 and start is None: start=x
        if v<=200 and start is not None:
            if x-start>30: runs.append((start,x-start))
            start=None
    if runs: print(y,runs)
