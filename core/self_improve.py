# -*- coding: utf-8 -*-
"""Zero · Self-improvement loop (acotado, auditable)."""
from __future__ import annotations
import json, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEEDBACK_LOG = ROOT / "memory" / "feedback_log.json"
IMPROVEMENT_LOG = ROOT / "memory" / "improvement_log.json"


def _load(p):
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def record_feedback(signal, detail="", context=""):
    """signal: 'good' | 'bad' | 'correction' | 'task_done' | 'task_failed'"""
    entries = _load(FEEDBACK_LOG)
    entries.append({"ts": time.time(), "signal": signal, "detail": detail, "context": context})
    _save(FEEDBACK_LOG, entries[-500:])
    # auto-apply acotado
    if signal == "correction" and detail:
        from . import companion
        companion.add_style_example(f"Corrección del usuario: {detail}")
        _log_improvement("style_example", detail)
    if signal == "task_failed":
        _log_improvement("task_failed", detail)


def _log_improvement(kind, detail):
    entries = _load(IMPROVEMENT_LOG)
    entries.append({"ts": time.time(), "kind": kind, "detail": detail})
    _save(IMPROVEMENT_LOG, entries[-500:])


def stats():
    fb = _load(FEEDBACK_LOG)
    from collections import Counter
    c = Counter(e["signal"] for e in fb)
    return {"total": len(fb), "by_signal": dict(c)}
