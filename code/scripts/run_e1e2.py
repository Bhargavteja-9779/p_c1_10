"""E1 (risk-prediction validity) + E2 (method comparison) + E3 (unit qualification / LFBC) under LOUO.
Usage: python scripts/run_e1e2.py mango|neo|corn [seeds]"""
import sys, time, os, warnings; sys.path.insert(0, '.')
warnings.filterwarnings('ignore')
import pandas as pd
from src.fleet import builders as B
from src.fleet.protocol import run_scenario, choose_master
OUT = '../results/e1e2'; os.makedirs(OUT, exist_ok=True)
which = sys.argv[1]; seeds = range(int(sys.argv[2]) if len(sys.argv) > 2 else 5)
jobs = {'mango': [('mango', s) for s in (2015, 2016, 2017, 2018, 2019, 2020)],
        'neo': [('neo', p) for p in ('oc', 'clay', 'ph', 'n', 'cec', 'sand')],
        'corn': [('corn', p) for p in ('moisture', 'oil', 'protein', 'starch')]}[which]
for kind, arg in jobs:
    f = f'{OUT}/{kind}_{arg}.csv'
    if os.path.exists(f):
        continue
    fl = B.mango(arg) if kind == 'mango' else B.neospectra(arg) if kind == 'neo' else B.corn(arg)
    master = choose_master(fl)
    t = time.time(); dfs = []
    for s in seeds:
        dfs.append(run_scenario(fl, master, seed=s, min_test=10 if kind == 'corn' else 20, min_pairs=5))
    pd.concat(dfs).to_csv(f, index=False)
    print(kind, arg, master, f'{time.time()-t:.0f}s', flush=True)
