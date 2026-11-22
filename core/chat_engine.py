# -*- coding: utf-8 -*-
"""Zero · Motor de chat (contexto de repo + LLM opcional OpenAI-compatible)."""
from __future__ import annotations
import json
from . import http, settings as S, github_client as GH
from . import companion


def build_repo_context(owner, repo, max_chars=6000):
    ctx = []
    r = GH.get_repo(owner, repo)
    if not r.ok:
        return f"Error obteniendo repo: {r.error}"
    d = r.data or {}
    ctx.append(f"Repo: {d.get('full_name')} — {d.get('description')}")
    ctx.append(f"Language: {d.get('language')} | Stars: {d.get('stargazers_count')} | Default branch: {d.get('default_branch')}")
    # README
    rd = GH.get_file(owner, repo, "README.md")
    if rd.ok and isinstance(rd.data, dict):
        content = rd.data.get("_decoded", "")
        if content:
            ctx.append("\n--- README.md ---\n" + content[:2000])
    # tree (top-level)
    tr = GH.get_tree(owner, repo)
    if tr.ok and isinstance(tr.data, dict):
        tree = tr.data.get("tree", [])
        files = [t["path"] for t in tree if t.get("type") == "blob"]
        ctx.append("\n--- Archivos (top 60) ---\n" + "\n".join(files[:60]))
    text = "\n".join(ctx)
    return text[:max_chars]


def llm_chat(messages, system=""):
    cfg = S.get_llm()
    if not cfg["base_url"] or not cfg["api_key"] or not cfg["model"]:
        return None
    url = cfg["base_url"].rstrip("/") + "/chat/completions"
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages)
    body = {"model": cfg["model"], "messages": msgs, "temperature": 0.4}
    r = http.request("POST", url, headers={"Authorization": f"Bearer {cfg['api_key']}"}, body=body, timeout=60.0)
    if not r.ok:
        return f"[LLM error] {r.error}"
    try:
        return r.data["choices"][0]["message"]["content"]
    except Exception:
        return f"[LLM parse error] {r.text[:300]}"


def answer(question, repo_ctx="", history=None):
    history = history or []
    system = companion.persona_text() + "\\n\\n" + ("Eres Zero, una mascota de escritorio especializada en repositorios de GitHub. "
              "Responde en español, conciso, basándote en el contexto del repo proporcionado. "
              "Si no hay contexto suficiente, dilo.")
    if repo_ctx:
        system += "\n\nCONTEXTO DEL REPO:\n" + repo_ctx
    msgs = [{"role": "user", "content": question}]
    # include recent history
    for h in (history or [])[-6:]:
        msgs.insert(0, h) if False else None
    res = llm_chat(msgs, system=system)
    if res is None:
        # no LLM configured: return context + hint
        return ("No hay modelo LLM configurado. Aquí está el contexto del repo:\n\n" + (repo_ctx or "(sin repo seleccionado)")
                + "\n\nConfigura un modelo en Ajustes (base URL + API key + modelo OpenAI-compatible).")
    return res
