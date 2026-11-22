"""Download registered datasets with checksum verification and a provenance manifest.

Usage:  python -m src.data.download corn tablets mango_v3
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

from src.data.registry import DATASETS

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "data" / "MANIFEST.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}


def fetch(name: str, retries: int = 4) -> Path:
    spec = DATASETS[name]
    dest = RAW / name / spec["filename"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    man = load_manifest()
    expected = spec.get("sha256") or man.get(name, {}).get("sha256")
    if dest.exists() and expected and sha256(dest) == expected:
        return dest
    for k in range(retries):
        try:
            req = urllib.request.Request(spec["url"], headers={"User-Agent": "research-repro/1.0"})
            with urllib.request.urlopen(req, timeout=600) as r, open(str(dest) + ".part", "wb") as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
            Path(str(dest) + ".part").replace(dest)
            break
        except Exception as e:  # noqa: BLE001
            if k == retries - 1:
                raise
            time.sleep(5 * (k + 1))
    digest = sha256(dest)
    if expected and digest != expected:
        raise RuntimeError(f"{name}: checksum mismatch {digest} != {expected}")
    if spec.get("md5"):
        h = hashlib.md5()
        with open(dest, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        if h.hexdigest() != spec["md5"]:
            raise RuntimeError(f"{name}: publisher MD5 mismatch")
    man[name] = {"file": str(dest.relative_to(ROOT)), "sha256": digest, "bytes": dest.stat().st_size,
                 "url": spec["url"], "licence": spec["licence"], "citation": spec["citation"],
                 "downloaded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                 "checksum_source": "publisher" if (spec.get("sha256") or spec.get("md5")) else "first-download"}
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(man, indent=2))
    return dest


if __name__ == "__main__":
    for n in sys.argv[1:] or list(DATASETS):
        p = fetch(n)
        print(n, "->", p)
