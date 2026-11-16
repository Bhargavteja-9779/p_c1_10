"""YAML configuration with mode (quick/full) overrides and dotted CLI overrides."""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml


def deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def load_config(path: str | Path, mode: str = "full", overrides: list[str] | None = None) -> dict:
    """Load ``path``; if it has a ``modes: {quick: {...}, full: {...}}`` block, merge the chosen mode."""
    with open(path) as f:
        cfg = yaml.safe_load(f) or {}
    modes = cfg.pop("modes", {}) or {}
    if mode not in ("quick", "full"):
        raise ValueError(f"mode must be quick or full, got {mode!r}")
    cfg = deep_merge(cfg, modes.get(mode, {}))
    cfg["mode"] = mode
    for item in overrides or []:
        key, _, raw = item.partition("=")
        node = cfg
        parts = key.split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = yaml.safe_load(raw)
    return cfg


def get(cfg: dict, dotted: str, default: Any = None) -> Any:
    node = cfg
    for p in dotted.split("."):
        if not isinstance(node, dict) or p not in node:
            return default
        node = node[p]
    return node
