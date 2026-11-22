# -*- coding: utf-8 -*-
"""Zero · Ajustes (token de GitHub, modelo LLM opcional)."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SETTINGS_FILE = ROOT / "database" / "settings" / "zero.json"


def load() -> dict:
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save(data: dict) -> None:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_token() -> str:
    import os
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if t:
        return t
    return load().get("github_token", "")


def set_token(t: str) -> None:
    d = load()
    d["github_token"] = t
    save(d)


def get_llm() -> dict:
    d = load()
    return {
        "base_url": d.get("llm_base_url", ""),
        "api_key": d.get("llm_api_key", ""),
        "model": d.get("llm_model", ""),
    }


def set_llm(base_url="", api_key="", model="") -> None:
    d = load()
    d["llm_base_url"] = base_url
    d["llm_api_key"] = api_key
    d["llm_model"] = model
    save(d)
