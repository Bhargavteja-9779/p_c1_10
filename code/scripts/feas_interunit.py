"""Feasibility: magnitude of inter-unit prediction error in the mango fleet."""
import sys; sys.path.insert(0,'.')
import numpy as np, pandas as pd
from src.data.loaders import load_mango
from src.preprocessing.spectral import savgol
from src.models.pls import PLS1, select_n_components
d=load_mango('v4'); m=d.meta.copy(); m['dm']=d.Y.dm.values
keep=(d.wl>=684)&(d.wl<=990)
r=(d.wl>=660)&(d.wl<=1014); Z=savgol(d.X[:,r],13,2,2)[:,keep[r]]
ok=(m.outlier_flag==0).values
for season in [2016,2017,2018]:
    ms=m[(m.season==season)&ok]
    ct=ms.groupby('instrument').sample_id.nunique().sort_values(ascending=False)
    master=ct.index[0]
    fr=ms[ms.instrument==master].sample_id.unique()
    rng=np.random.default_rng(0); rng.shuffle(fr)
    tr=set(fr[:len(fr)//2]); te=set(fr[len(fr)//2:])
    itr=ms.index[(ms.instrument==master)&ms.sample_id.isin(tr)]
    a,_=select_n_components(Z[itr],m.dm[itr].values,m.sample_id[itr].values,20)
    mod=PLS1(a).fit(Z[itr],m.dm[itr].values)
    print(f'\nseason {season} master {master} n_tr={len(itr)} LV={a}')
    rows=[]
    for u in ct.index:
        ite=ms.index[(ms.instrument==u)&ms.sample_id.isin(te)]
        if len(ite)<40: continue
        p=mod.predict(Z[ite]); y=m.dm[ite].values; e=p-y
        rows.append((u,len(ite),ms.loc[ite].sample_id.nunique(),np.sqrt(np.mean(e**2)),e.mean(),e.std()))
    print(pd.DataFrame(rows,columns=['unit','n','fruit','rmse','bias','sep']).round(3).to_string(index=False))
