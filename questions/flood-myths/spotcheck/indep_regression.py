"""Independent refit (statsmodels + own Conley) of the flood-myths models. Exploratory variants are labelled."""
import sys, json, math, numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import norm, t as tdist
D,J,OUT=sys.argv[1:4]; R=6371.0088
rr=pd.read_stata(f'{D}/Berezkin_groups_Regressions_Ready.dta')
mot=pd.read_stata(f'{D}/Motifs_Berezkin_groups.dta',convert_categoricals=False)
NB=["c2","c4","c7","c9a","c10","c10a","c12a","c12b","c13","c14","b7b","b7d","b52a","g9a","i81a","k38d","l28a"]
EXPLICIT=["c4","c7","c9a","c10","c10a","c12a","g9a","b7d","l28a","c2"]  # titles/descs centred on a flood
for c in NB+["c3","c5a"]: mot[c]=pd.to_numeric(mot[c],errors='coerce').fillna(0)
mot['nb']=mot[NB].sum(1); mot['ex']=mot[EXPLICIT].sum(1)
need=["latitude_forgeo","longitude_forgeo","motifs_total","lnnmbr_title","lnyear_firstpub","lnriver_dist_bere","lnbdisttoquake1000","avtemp200_bere"]
df=rr.merge(mot[['oid','nb','ex','c3','c5a']],on='oid').dropna(subset=need).reset_index(drop=True)
mp=pd.DataFrame(json.load(open(J))['map_points'])
assert len(mp)==len(df) and np.allclose(mp.lat,df.latitude_forgeo.round(2)) and (mp.g.values==df.group_Berezkin.astype(str).values).all()
sea=pd.read_csv(f'{OUT}/exposure_sea_only.csv'); assert (sea.g.values==mp.g.values).all()
# exposures: re-derive coastal flag and d120 from map_points (study values, rounded) and my sea-only version
df['d120']=mp.d120.values; df['coastal']=mp.c.values
df['d120_sea']=sea.d120_sea.values; df['coastal_sea']=sea.coastal_sea.values; df['dist_sea']=sea.dist_sea_km.values
comp=pd.read_csv(f'{OUT}/exposure_components.csv')
# need dist_coast_km for control: recompute from study grid not available here -> use study's approach via sea file? use any-water distance from components file
df['dist_any']=np.nan
S=json.load(open(J))
print("N=",len(df)," coastal=",int(df.coastal.sum()))
df['share']=df.nb/df.motifs_total.clip(lower=1); df['ex_share']=df.ex/df.motifs_total.clip(lower=1)
df['anynb']=(df.nb>0).astype(float)
for c in ['share','ex_share','flood_related','earthquake_related','sea_related','fire_related']:
    s=df[c].astype(float); df[c+'_z']=(s-s.mean())/s.std(ddof=0)
print("prevalence any NB: global %.4f coastal %.4f inland %.4f"%(df.anynb.mean(),df[df.coastal==1].anynb.mean(),df[df.coastal==0].anynb.mean()))
print("corr(nb share, flood_related) all=%.3f ; share of groups with flood_related>0 = %.3f; any NB =%.3f"%(df.share.corr(df.flood_related),(df.flood_related>0).mean(),df.anynb.mean()))
print("c5a groups by continent:",df[df.c5a>0].continent_bere.value_counts().to_dict())
print("c3 groups by continent:",df[df.c3>0].continent_bere.value_counts().to_dict())
def gcmat(la,lo):
    la,lo=np.radians(la),np.radians(lo); x=np.column_stack([np.cos(la)*np.cos(lo),np.cos(la)*np.sin(lo),np.sin(la)])
    return R*np.arccos(np.clip(x@x.T,-1,1))
def fit(sub,y,x,ctrl,fe='language1',label='',stdx=True,distcol='dist_coast'):
    sub=sub.reset_index(drop=True)
    xv=sub[x].astype(float); xs=(xv-xv.mean())/xv.std(ddof=0) if stdx else xv
    X=pd.DataFrame({'x':xs})
    for c in ctrl: X[c]=sub[c].astype(float)
    if fe: X=pd.concat([X,pd.get_dummies(sub[fe].astype(str),prefix='fe',drop_first=True,dtype=float)],axis=1)
    X=sm.add_constant(X)
    yy=sub[y].astype(float)
    m=sm.OLS(yy,X).fit(cov_type='cluster',cov_kwds={'groups':pd.factorize(sub.language1.astype(str))[0]},use_t=True)
    # own Conley 1000 km Bartlett
    Dm=gcmat(sub.latitude_forgeo.values,sub.longitude_forgeo.values); e=m.resid.values; Xa=X.values
    XtXi=np.linalg.pinv(Xa.T@Xa); Xe=Xa*e[:,None]; out={}
    for cut in (500,1000):
        W=np.maximum(0,1-Dm/cut); V=XtXi@(Xe.T@W@Xe)@XtXi; out[cut]=math.sqrt(V[1,1])
    b=m.params['x']; se=m.bse['x']; G=sub.language1.nunique(); fam=sub.language1.value_counts()
    r=dict(label=label,n=len(sub),G=G,singletons=int((fam==1).sum()),b=b,se_cl=se,p_cl=m.pvalues['x'],ci_cl=(b-tdist.ppf(.975,G-1)*se,b+tdist.ppf(.975,G-1)*se),
           se_c1000=out[1000],p_c1000=2*norm.sf(abs(b/out[1000])),se_c500=out[500],sd_x=float(xv.std(ddof=0)))
    return r
def show(r):
    print(f"{r['label']:62s} n={r['n']:3d} G={r['G']:2d} sing={r['singletons']:2d} b={r['b']:+.4f} se_cl={r['se_cl']:.4f} p_cl={r['p_cl']:.3f} CI_cl=[{r['ci_cl'][0]:+.3f},{r['ci_cl'][1]:+.3f}] se_c1k={r['se_c1000']:.4f} p_c1k={r['p_c1000']:.3f} sd_x={r['sd_x']:.3f}")
    return r
# controls as in protocol; dist_coast from study: reconstruct log_dist_coast via study's grid is in exposure files? use components file dist? Not there -> recompute quickly:
import h5py
from scipy.spatial import cKDTree
f=h5py.File(f'{D}/ETOPO_2022_v1_60s_N90W180_bed.nc','r'); lat=f['lat'][:]; lon=f['lon'][:]
z5=f['z'][:].astype(np.float32).reshape(2160,5,4320,5).mean(axis=(1,3)); lat5=lat.reshape(2160,5).mean(1); lon5=lon.reshape(4320,5).mean(1)
xyz=lambda la,lo: np.column_stack([np.cos(np.radians(la))*np.cos(np.radians(lo)),np.cos(np.radians(la))*np.sin(np.radians(lo)),np.sin(np.radians(la))])
oy,ox=np.where(z5<0); T=cKDTree(xyz(lat5[oy],lon5[ox])); d,_=T.query(xyz(df.latitude_forgeo.values,df.longitude_forgeo.values))
df['dist_coast']=2*R*np.arcsin(np.clip(d/2,0,1)); assert ((df.dist_coast<=150).astype(int)==df.coastal).all()
df['log_dist_coast']=np.log1p(df.dist_coast); df['log_dist_sea']=np.log1p(df.dist_sea)
df['log_mt']=np.log1p(df.motifs_total.astype(float)); df['abs_lat']=df.latitude_forgeo.abs()
df['ld120']=np.log1p(df.d120); df['ld120_sea']=np.log1p(df.d120_sea)
df['neg_lnquake']=-df.lnbdisttoquake1000; df['neg_ldc']=-df.log_dist_coast
M1=['log_dist_coast','lnnmbr_title','lnyear_firstpub','log_mt']; M2=M1+['lnriver_dist_bere','lnbdisttoquake1000','avtemp200_bere','abs_lat']
co=df[df.coastal==1]
print("\n--- Independent refit of the study's models (statsmodels) ---")
res={}
res['M4']=show(fit(co,'share_z','ld120',M2,label='Coastal M4 nb_share_z ~ log d120 (per SD of x)'))
show(fit(co,'share_z','ld120',M2,label='Coastal M4, x NOT standardised (per log unit)',stdx=False))
show(fit(co,'share_z','ld120',M2,fe='continent_bere',label='Coastal M3'))
show(fit(co,'anynb','ld120',M2,label='Coastal M4 any_nb (LPM)'))
show(fit(co,'flood_related_z','ld120',M2,label='Coastal M4 flood_related_z'))
nf=co[(co.c3==0)&(co.c5a==0)]
show(fit(nf,'share_z','ld120',M2,label='Noah-free (no c3,c5a) coastal M4'))
print("\n--- Calibration controls as coded (global, lang FE, sampling controls + abs_lat only) ---")
show(fit(df,'earthquake_related_z','neg_lnquake',['lnnmbr_title','lnyear_firstpub','log_mt','abs_lat'],label='PC1 earthquake ~ -ln quake dist (as coded)'))
show(fit(df,'sea_related_z','neg_ldc',['lnnmbr_title','lnyear_firstpub','log_mt','abs_lat'],label='PC2 sea ~ -log dist coast (as coded)'))
print("\n--- EXPLORATORY (spot-check only): calibration in the primary sample/spec ---")
M2q=[c for c in M2 if c!='lnbdisttoquake1000']
show(fit(co,'earthquake_related_z','neg_lnquake',M2q,label='PC1 in coastal sample, M4 controls'))
show(fit(df,'earthquake_related_z','neg_lnquake',M2q,label='PC1 global, M4 controls'))
show(fit(df,'sea_related_z','neg_ldc',[c for c in M2 if c!='log_dist_coast'],label='PC2 global, M4 controls'))
print("\n--- EXPLORATORY sensitivity (not in locked protocol) ---")
low=co[co.abs_lat<50]; show(fit(low,'share_z','ld120',M2,label='Coastal M4, |lat|<50 only'))
show(fit(low,'flood_related_z','ld120',M2,label='Coastal M4 flood_related, |lat|<50'))
trop=co[co.abs_lat<30]; show(fit(trop,'share_z','ld120',M2,label='Coastal M4, |lat|<30 only'))
cs=df[df.coastal_sea==1]
M2s=['log_dist_sea']+M2[1:]
show(fit(cs,'share_z','ld120_sea',M2s,label='Connected-sea coastal M4 (drops Caspian/Great Lakes etc.)'))
show(fit(cs,'flood_related_z','ld120_sea',M2s,label='Connected-sea coastal M4 flood_related'))
show(fit(co,'ex_share_z','ld120',M2,label='Coastal M4, explicit-flood motifs only (10)'))
nf2=co[co.c3==0]; show(fit(nf2,'share_z','ld120',M2,label='Noah-free defined by c3 only'))
# singleton families & within-family variation
fam=co.language1.value_counts(); print("\ncoastal families:",len(fam)," singletons:",int((fam==1).sum())," societies in families>=2:",int(fam[fam>=2].sum()))
w=co.groupby('language1').ld120.transform(lambda s:s-s.mean()); print("SD of log d120 total %.3f, within-family %.3f"%(co.ld120.std(ddof=0),w.std(ddof=0)))
# quartile check
q=np.quantile(co.d120,[0,.25,.5,.75,1]); print("quartile edges",q)
for i in range(4):
    m=(co.d120>=q[i])&((co.d120<=q[i+1]) if i==3 else (co.d120<q[i+1])); print(f"Q{i+1} n={m.sum()} anyNB={co[m].anynb.mean()*100:.1f}%")
# power for primary
b=res['M4']; se=b['se_cl']
for eff in (0.10,0.15,0.20):
    for a in (0.05,0.01):
        zc=norm.ppf(1-a/2); print(f"power vs beta={eff} SD/SD at alpha={a} (cluster SE {se:.4f}): {norm.sf(zc-eff/se):.2f}")
print("MDE 80%% power alpha .05: %.3f ; alpha .01: %.3f"%((1.96+0.84)*se,(2.576+0.84)*se))
