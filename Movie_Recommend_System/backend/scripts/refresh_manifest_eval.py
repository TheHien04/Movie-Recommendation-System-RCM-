#!/usr/bin/env python3
"""Refresh offline_eval block in artifacts manifest without full retrain."""
from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from scripts.train_models import ARTIFACT_DIR, _offline_eval  # noqa: E402

manifest_path = ARTIFACT_DIR / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
eval_metrics = _offline_eval()
manifest["offline_eval"] = eval_metrics
manifest["tuned_ndcg"] = eval_metrics.get("avg_ndcg@5")
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(eval_metrics, indent=2))
