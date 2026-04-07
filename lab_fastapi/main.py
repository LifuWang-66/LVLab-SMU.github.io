"""Unified FastAPI entrypoint for the lab website + GPU monitor backend.

Running this app gives:
- Original LV-Lab pages (SMU + NUS) served by FastAPI
- GPU monitor API/session endpoints under /api/*
- GPU monitor page under /SMU/gpu-monitor.html and /gpu-monitor
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GPU_BACKEND_ROOT = ROOT / 'SMU' / 'gpu-monitor-backend'

if str(GPU_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(GPU_BACKEND_ROOT))

# Reuse the already-integrated FastAPI app from SMU/gpu-monitor-backend.
from app.main import app  # noqa: E402,F401
