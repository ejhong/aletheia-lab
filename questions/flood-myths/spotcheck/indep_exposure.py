"""Independent recomputation of drowned-shelf exposure (spot check, not the study's code).
(1) Full 1-arc-minute ETOPO grid, brute-force great-circle distances, for a stratified sample of coastal societies + named checks.
(2) Connected-component check at 5-arc-minute: how much of each society's 'ocean'/'drowned' area lies in water bodies
    not connected to the world ocean (Caspian, Great Lakes, depressions)."""
import sys, json, math, numpy as np, pandas as pd, h5py
from scipy import ndimage
from scipy.spatial import cKDTree
D=sys.argv[1]; J=sys.argv[2]; OUT=sys.argv[3]
R=6371.0088
j=json.load(open(J)); mp=pd.DataFrame(j['map_points'])
f=h5py.File(f'{D}/ETOPO_2022_v1_60s_N90W180_bed.nc','r')
lat=f['lat'][:]; lon=f['lon'][:]
def gc(lat1,lon1,lat2,lon2):
    p1,p2=np.radians(lat1),np.radians(lat2); dl=np.radians(lon2-lon1)
    a=np.sin((p2-p1)/2)**2+np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2
    return 2*R*np.arcsin(np.sqrt(np.clip(a,0,1)))
dA=math.radians(1/60)
def full_res(la,lo,rad=250.0):
    dlat=rad/111.0+0.1
    i0=max(0,np.searchsorted(lat,la-dlat)); i1=min(len(lat),np.searchsorted(lat,la+dlat)+1)
    dlon=min(180,rad/(111.0*max(0.05,math.cos(math.radians(min(89.9,abs(la)+dlat)))))+0.1)
    # longitude indices with wrap
    lo_idx=np.where(np.abs(((lon-lo+180)%360)-180)<=dlon)[0]
    z=f['z'][i0:i1,:][:,lo_idx].astype(float)
    LA=lat[i0:i1][:,None]; LO=lon[lo_idx][None,:]
    d=gc(la,lo,LA,LO)
    area=(R*dA)*(R*dA*np.cos(np.radians(LA)))*np.ones_like(z)
    within=d<=rad
    drown=within&(z>=-120)&(z<0)
    ocean=(z<0)
    dc=d[ocean].min() if ocean.any() else np.nan
    return float(area[drown].sum()), float(dc), float(area[within&(z>=-60)&(z<0)].sum())
# ---- sample
rng=np.random.default_rng(7)
co=mp[mp.c==1].copy()
q=np.quantile(co.d120,[0,.25,.5,.75,1]); co['q']=np.digitize(co.d120,q[1:-1],right=False)
samp=pd.concat([g.sample(6,random_state=int(rng.integers(1e6))) for _,g in co.groupby('q')])
named=['Dutch, Flemish, Frisians','Muslim Malay','Lampung; S. Sumatra Malay','Batak; Gayo','Hawaii','Mapuche','Northern Peru: Costa','Kalmyk','Huron, Wyandot','Ojibwa (Eastern)','Five Nations Iroquois','St.Lawrence Eskimo','Swampy Cree (Western)','Polar Eskimo','West Greenland Eskimo']
samp=pd.concat([samp,mp[mp.g.isin(named)]]).drop_duplicates('g')
rows=[]
for _,r in samp.iterrows():
    a,dc,a60=full_res(r.lat,r.lon)
    rows.append(dict(g=r.g,lat=r.lat,lon=r.lon,coastal=r.c,study_d120=r.d120,mine_d120_1min=round(a),ratio=(a/r.d120 if r.d120>0 else np.nan),mine_distcoast_km=round(dc,1),mine_d60=round(a60)))
S=pd.DataFrame(rows)
pd.set_option('display.width',250); pd.set_option('display.max_rows',100)
print(S.to_string(index=False))
S.to_csv(f'{OUT}/exposure_sample.csv',index=False)
s=S[S.study_d120>0]
print('\nSample n=',len(S),' median ratio mine/study=',round(s.ratio.median(),3),' IQR',np.round(s.ratio.quantile([.25,.75]).values,3),
      ' Spearman',round(pd.Series(s.mine_d120_1min).corr(s.study_d120,method='spearman'),4),' Pearson log',round(np.corrcoef(np.log1p(s.mine_d120_1min),np.log1p(s.study_d120))[0,1],4))
# ---- connected components at 5-arcmin (same block-averaging as study)
z=f['z'][:].astype(np.float32)
z5=z.reshape(2160,5,4320,5).mean(axis=(1,3)); del z
lat5=lat.reshape(2160,5).mean(1); lon5=lon.reshape(4320,5).mean(1)
oc=z5<0
lab,nlab=ndimage.label(oc,structure=np.ones((3,3)))
# merge across dateline
for a,b in zip(lab[:,0],lab[:,-1]):
    if a and b and a!=b: lab[lab==b]=a
sizes=np.bincount(lab.ravel()); sizes[0]=0; main=sizes.argmax()
print('\nocean components:',nlab,' main component cells',sizes[main],' share of z<0 cells in main',round(sizes[main]/oc.sum(),4))
rowA=(R*math.radians(5/60))**2*np.cos(np.radians(lat5))
oy,ox=np.where(oc); xyz=lambda la,lo: np.column_stack([np.cos(np.radians(la))*np.cos(np.radians(lo)),np.cos(np.radians(la))*np.sin(np.radians(lo)),np.sin(np.radians(la))])
T=cKDTree(xyz(lat5[oy],lon5[ox])); ismain=lab[oy,ox]==main; zz=z5[oy,ox]; ar=rowA[oy]
mainT=cKDTree(xyz(lat5[oy][ismain],lon5[ox][ismain]))
P=xyz(mp.lat.values,mp.lon.values)
dch,_=mainT.query(P); mp['dist_main_ocean_km']=2*R*np.arcsin(np.clip(dch/2,0,1))
r250=2*math.sin(250/(2*R))
dm=[];dn=[]
for idx in T.query_ball_point(P,r250):
    idx=np.asarray(idx,int)
    if len(idx)==0: dm.append(0);dn.append(0);continue
    sel=(zz[idx]>=-120)
    dm.append(ar[idx][sel&ismain[idx]].sum()); dn.append(ar[idx][sel&~ismain[idx]].sum())
mp['d120_main']=dm; mp['d120_nonmain']=dn
mp['d120_recomp']=mp.d120_main+mp.d120_nonmain
print('max |recomputed 5-arcmin - study d120| =',float((mp.d120_recomp-mp.d120).abs().max()))
co=mp[mp.c==1]
bad=co[(co.d120_nonmain>0.2*co.d120)|(co.dist_main_ocean_km>150)]
print('\nCoastal societies (<=150 km of any z<0 cell) whose drowned area is >20% non-ocean basin, or which are >150 km from the connected ocean:',len(bad))
print(bad[['g','lat','lon','d120','d120_main','d120_nonmain','dist_main_ocean_km','nb']].round(0).to_string(index=False))
print('\nAll societies classed coastal but >150 km from connected ocean:',int((co.dist_main_ocean_km>150).sum()))
print('Societies classed inland that are <=150 km from main ocean:',int(((mp.c==0)&(mp.dist_main_ocean_km<=150)).sum()))
mp.to_csv(f'{OUT}/exposure_components.csv',index=False)
