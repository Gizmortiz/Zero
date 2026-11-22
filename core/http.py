# -*- coding: utf-8 -*-
"""Zero · HTTP mínimo (stdlib)."""
from __future__ import annotations
import json, time, urllib.error, urllib.request
from dataclasses import dataclass, field


@dataclass
class HttpResult:
    ok: bool
    status: int
    data: object
    text: str
    elapsed_ms: int
    error: str = ""
    headers: dict = field(default_factory=dict)


def request(method, url, headers=None, body=None, timeout=25.0):
    hdrs = {"Accept": "application/json", "User-Agent": "Zero/1.0"}
    hdrs.update(headers or {})
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    t0 = time.perf_counter()
    status, raw, rh = 0, "", {}
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            raw = resp.read().decode("utf-8", "replace")
            rh = {str(k).lower(): str(v) for k, v in resp.headers.items()}
    except urllib.error.HTTPError as exc:
        status = exc.code
        try:
            rh = {str(k).lower(): str(v) for k, v in (exc.headers or {}).items()}
        except Exception:
            rh = {}
        try:
            raw = exc.read().decode("utf-8", "replace")
        except Exception:
            raw = ""
    except Exception as exc:
        ms = int((time.perf_counter() - t0) * 1000)
        return HttpResult(False, 0, None, "", ms, error=f"No se pudo conectar: {exc}")
    ms = int((time.perf_counter() - t0) * 1000)
    try:
        parsed = json.loads(raw) if raw else None
    except ValueError:
        parsed = None
    ok = 200 <= status < 300
    err = "" if ok else f"Error HTTP {status}. {(raw or '')[:200]}"
    return HttpResult(ok, status, parsed, raw, ms, err, rh)
