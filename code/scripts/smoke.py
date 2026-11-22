import sys, time; sys.path.insert(0,'.')
import pandas as pd
from src.fleet import builders as B
from src.fleet.protocol import run_scenario
pd.set_option('display.width',250)
t=time.time()
fl=B.mango(2017); cov=fl.coverage()>0; master=cov.sum(0).idxmax(); print(fl.X.shape, master)
df=run_scenario(fl, master, seed=0)
cols=[c for c in df.columns if c.startswith('rmse|') or c.startswith('pred') and 'Units' not in c]
print(df[['target','n_fleet','n_test_items','n_pairs_target']+cols].round(2).T.to_string())
print(time.time()-t)
