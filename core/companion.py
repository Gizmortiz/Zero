# -*- coding: utf-8 -*-
"""Zero · Companion core: persona + prompt versionado + memoria de estilo."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "prompts"
STYLE_FILE = ROOT / "memory" / "style_layer.json"
VERSIONS_FILE = ROOT / "memory" / "prompt_versions.json"


def _ensure():
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    (ROOT / "memory").mkdir(parents=True, exist_ok=True)


def list_versions():
    _ensure()
    if not VERSIONS_FILE.exists():
        return ["companion_v1"]
    try:
        return json.loads(VERSIONS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return ["companion_v1"]


def load_prompt(version="companion_v1"):
    _ensure()
    p = PROMPTS_DIR / f"{version}.txt"
    if not p.exists():
        p = PROMPTS_DIR / "companion_v1.txt"
    base = p.read_text(encoding="utf-8") if p.exists() else ""
    # style layer (auto-mejorado) se concatena
    style = ""
    if STYLE_FILE.exists():
        try:
            d = json.loads(STYLE_FILE.read_text(encoding="utf-8"))
            examples = d.get("examples", [])
            if examples:
                style = "\n\nEjemplos aprendidos (estilo):\n" + "\n".join(f"- {e}" for e in examples[-10:])
        except Exception:
            pass
    return base + style


def current_version():
    vs = list_versions()
    return vs[-1] if vs else "companion_v1"


def register_version(version, note=""):
    _ensure()
    vs = list_versions()
    if version not in vs:
        vs.append(version)
    VERSIONS_FILE.write_text(json.dumps(vs, ensure_ascii=False, indent=2), encoding="utf-8")
    # log
    log = ROOT / "memory" / "prompt_change_log.json"
    entries = []
    if log.exists():
        try:
            entries = json.loads(log.read_text(encoding="utf-8"))
        except Exception:
            entries = []
    entries.append({"version": version, "note": note})
    log.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def add_style_example(example):
    _ensure()
    d = {}
    if STYLE_FILE.exists():
        try:
            d = json.loads(STYLE_FILE.read_text(encoding="utf-8"))
        except Exception:
            d = {}
    examples = d.get("examples", [])
    examples.append(example)
    d["examples"] = examples[-50:]
    STYLE_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def persona_text():
    return load_prompt(current_version())
