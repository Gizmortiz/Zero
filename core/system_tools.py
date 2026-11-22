# -*- coding: utf-8 -*-
"""Zero · Tools del sistema (shell, archivos, procesos) con permisos."""
from __future__ import annotations
import os, subprocess, sys
from pathlib import Path
from . import self_improve

ROOT = Path(__file__).resolve().parent.parent
ALLOWED_ROOTS = [Path("C:/"), Path.home()]


def _allowed(path):
    try:
        p = Path(path).resolve()
        return any(str(p).lower().startswith(str(r).lower()) for r in ALLOWED_ROOTS)
    except Exception:
        return False


def run_command(cmd, cwd=None, timeout=30, confirm_callback=None):
    """Ejecuta comando shell. confirm_callback(cmd) debe retornar True para permitir."""
    if confirm_callback is not None and not confirm_callback(cmd):
        return {"ok": False, "error": "No autorizado por el usuario."}
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return {"ok": r.returncode == 0, "code": r.returncode,
                "stdout": r.stdout[:4000], "stderr": r.stderr[:2000]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Timeout"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def read_file(path):
    if not _allowed(path):
        return {"ok": False, "error": "Ruta no permitida."}
    try:
        p = Path(path)
        return {"ok": True, "content": p.read_text(encoding="utf-8", errors="replace")[:20000]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def write_file(path, content, confirm_callback=None):
    if not _allowed(path):
        return {"ok": False, "error": "Ruta no permitida."}
    if confirm_callback is not None and not confirm_callback(path):
        return {"ok": False, "error": "No autorizado."}
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        self_improve.record_feedback("task_done", detail=f"write {path}")
        return {"ok": True, "path": str(p)}
    except Exception as e:
        self_improve.record_feedback("task_failed", detail=f"write {path}: {e}")
        return {"ok": False, "error": str(e)}


def list_dir(path):
    if not _allowed(path):
        return {"ok": False, "error": "Ruta no permitida."}
    try:
        p = Path(path)
        items = [{"name": e.name, "is_dir": e.is_dir()} for e in p.iterdir()]
        return {"ok": True, "items": items[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def list_processes():
    try:
        r = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=15)
        return {"ok": True, "output": r.stdout[:8000]}
    except Exception as e:
        return {"ok": False, "error": str(e)}
