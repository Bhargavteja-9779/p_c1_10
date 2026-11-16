"""Deterministic seeding across Python, NumPy and (optionally) PyTorch.

Seeds are always taken from the experiment configuration (pre-registered list);
they are never chosen after looking at results.
"""
from __future__ import annotations

import os
import random

import numpy as np


def set_seed(seed: int, deterministic_torch: bool = True) -> np.random.Generator:
    """Seed all RNGs and return a NumPy Generator bound to ``seed``."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed % (2**32 - 1))
    try:
        import torch

        torch.manual_seed(seed)
        if deterministic_torch:
            torch.use_deterministic_algorithms(True, warn_only=True)
            if hasattr(torch.backends, "cudnn"):
                torch.backends.cudnn.deterministic = True
                torch.backends.cudnn.benchmark = False
    except ImportError:  # torch is optional
        pass
    return np.random.default_rng(seed)


def child_seed(base_seed: int, *keys: object) -> int:
    """Derive a reproducible child seed from a base seed and arbitrary keys.

    Uses NumPy's SeedSequence so that (base_seed, keys) -> seed is stable across
    platforms and Python hash randomisation.
    """
    entropy = [int(base_seed)] + [int.from_bytes(str(k).encode(), "little") % (2**32) for k in keys]
    return int(np.random.SeedSequence(entropy).generate_state(1)[0])
