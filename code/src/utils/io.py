"""Machine-readable result writing (CSV/JSON) plus provenance metadata.

All numbers that appear in the manuscript must come from files written here.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]  # repository root (…/p_c1_10)


def _jsonable(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"not JSON serialisable: {type(o)}")


def write_json(obj, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(obj, f, indent=2, default=_jsonable, sort_keys=False)
    os.replace(tmp, path)


def read_json(path: str | Path):
    with open(path) as f:
        return json.load(f)


def write_csv(df: pd.DataFrame, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    os.close(fd)
    df.to_csv(tmp, index=False)
    os.replace(tmp, path)


def git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def provenance() -> dict:
    import platform

    meta = {"timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "git_commit": git_commit(),
            "python": platform.python_version(), "platform": platform.platform()}
    for mod in ("numpy", "scipy", "sklearn", "pandas", "torch", "statsmodels", "matplotlib"):
        try:
            meta[mod] = __import__(mod).__version__
        except Exception:
            meta[mod] = None
    return meta
