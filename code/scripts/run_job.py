"""One E1-E3 job (v2 protocol). Usage: python scripts/run_job.py KIND ARG SEEDS GROUPED   (GROUPED: none|population)"""
import sys, os, time, warnings; sys.path.insert(0, '.'); warnings.filterwarnings('ignore')
import pandas as pd
from src.fleet import builders as B
from src.fleet.protocol import run_scenario, choose_master
kind, arg, seeds, grouped = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
rank = int(sys.argv[5]) if len(sys.argv) > 5 else 1
OUT = '../results/e1e2_v3'; os.makedirs(OUT, exist_ok=True)
f = f'{OUT}/{kind}_{arg}_{grouped}' + (f'_m{rank}' if rank > 1 else '') + '.csv'
if os.path.exists(f):
    sys.exit(0)
fl = B.mango(int(arg)) if kind == 'mango' else B.neospectra(arg) if kind == 'neo' else B.corn(arg)
master = choose_master(fl, rank); t = time.time()
df = pd.concat([run_scenario(fl, master, seed=s, min_test=10 if kind == 'corn' else 20, grouped=None if grouped == 'none' else grouped)
                for s in range(seeds)])
df.to_csv(f + '.tmp', index=False); os.replace(f + '.tmp', f)
print(kind, arg, grouped, master, f'{time.time()-t:.0f}s', flush=True)
