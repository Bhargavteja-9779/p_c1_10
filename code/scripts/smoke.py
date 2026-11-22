import sys, time; sys.path.insert(0,'.')
import pandas as pd, numpy as np
from src.fleet import builders as B
from src.fleet.protocol import run_scenario, choose_master
pd.set_option('display.width',250)
t=time.time()
name=sys.argv[1]
fl=B.mango(int(name)) if name.isdigit() else (B.neospectra(sys.argv[2]) if name=='neo' else B.corn(sys.argv[2]))
master=choose_master(fl); print(fl.X.shape, master)
df=run_scenario(fl, master, seed=0)
cols=[c for c in df.columns if (c.startswith('rmse') or c.startswith('pred')) and 'Units' not in c and 'all|' not in c]
print(df[['target','n_fleet','n_test_items','n_test_paired_items','n_pairs_target']+cols].round(2).T.to_string())
print(time.time()-t)
