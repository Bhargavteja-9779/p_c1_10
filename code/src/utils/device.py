"""Hardware detection: CPU, CUDA or Apple-Silicon MPS (never assumes NVIDIA)."""
from __future__ import annotations

import os
import platform


def detect_device(prefer: str = "auto") -> str:
    """Return 'cuda', 'mps' or 'cpu' depending on availability and preference."""
    try:
        import torch
    except ImportError:
        return "cpu"
    if prefer in ("cpu",):
        return "cpu"
    if torch.cuda.is_available() and prefer in ("auto", "cuda"):
        return "cuda"
    mps = getattr(torch.backends, "mps", None)
    if mps is not None and mps.is_available() and prefer in ("auto", "mps"):
        return "mps"
    return "cpu"


def hardware_summary() -> dict:
    info = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "processor": platform.processor() or platform.machine(),
        "cpu_count": os.cpu_count(),
    }
    try:
        import torch

        info.update({"torch": torch.__version__, "device": detect_device(), "torch_threads": torch.get_num_threads()})
    except ImportError:
        info.update({"torch": None, "device": "cpu"})
    return info
