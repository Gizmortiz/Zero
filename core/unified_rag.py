# -*- coding: utf-8 -*-
"""Zero · RAG unificado (federado): I-Pet (SQLite FTS) + Zero (LlamaIndex vector).

Fusión con Reciprocal Rank Fusion (RRF) para combinar scores incompatibles.
Cada resultado lleva 'source' para provenance.
"""
from __future__ import annotations
import json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IPET_ROOT = Path(r"C:\I-Pet")


def _ipet_search(query, k=5):
    """Consulta el RAG de I-Pet. Devuelve lista de {source, path, text, score}."""
    results = []
    # Intento 1: importar módulo
    if IPET_ROOT.exists() and str(IPET_ROOT) not in sys.path:
        sys.path.insert(0, str(IPET_ROOT))
    try:
        import core.rag_sql as rag_sql  # type: ignore
        # API hipotética: search(query, k) -> list of dicts
        hits = rag_sql.search(query, k) if hasattr(rag_sql, "search") else []
        for h in (hits or []):
            results.append({"source": "ipet", "path": h.get("path", ""), "text": h.get("text", ""), "score": 0.0})
        if results:
            return results
    except Exception:
        pass
    # Intento 2: CLI
    try:
        proc = subprocess.run(
            [str(IPET_ROOT / ".venv" / "Scripts" / "python.exe") if (IPET_ROOT / ".venv" / "Scripts" / "python.exe").exists() else "python",
             "-m", "core.rag_cli", "search", query, "-k", str(k)],
            cwd=str(IPET_ROOT), capture_output=True, text=True, timeout=30,
        )
        # parseo best-effort: cada línea con [path]
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line and "[" in line and "]" in line:
                results.append({"source": "ipet", "path": line, "text": line, "score": 0.0})
    except Exception:
        pass
    return results[:k]


def _zero_search(owner, repo, query, k=5):
    """Consulta el RAG vectorial de Zero."""
    results = []
    try:
        from . import repo_rag
        idx = repo_rag.build_index(owner, repo)
        if idx is None:
            return results
        text = repo_rag.query(idx, query, top_k=k)
        # parseo por bloques '--- path ---'
        blocks = text.split("--- ")
        for b in blocks:
            b = b.strip()
            if not b:
                continue
            lines = b.split("\n", 1)
            path = lines[0].strip().rstrip(" -")
            body = lines[1].strip() if len(lines) > 1 else ""
            results.append({"source": f"zero:{owner}/{repo}", "path": path, "text": body, "score": 0.0})
    except Exception as e:
        results.append({"source": "zero", "path": "", "text": f"[error] {e}", "score": 0.0})
    return results[:k]


def rrf_fuse(result_lists, k=60):
    """Reciprocal Rank Fusion: combina listas de resultados por rango."""
    scores = {}
    items = {}
    for lst in result_lists:
        for rank, item in enumerate(lst, start=1):
            key = (item["source"], item["path"], item["text"][:80])
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            items[key] = item
    fused = []
    for key, sc in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        it = dict(items[key])
        it["score"] = round(sc, 6)
        fused.append(it)
    return fused


def unified_retrieve(query, owner="", repo="", k=5, use_ipet=True, use_zero=True, audit=True):
    lists = []
    if use_ipet:
        lists.append(_ipet_search(query, k))
    if use_zero and owner and repo:
        lists.append(_zero_search(owner, repo, query, k))
    fused = rrf_fuse(lists)
    out = fused[:k]
    if audit:
        _audit(query, owner, repo, out)
    return out


def provenance_summary(results):
    from collections import Counter
    c = Counter(r["source"].split(":")[0] if ":" in r["source"] else r["source"] for r in results)
    return dict(c)


# --- Métricas sobre golden set ---
def load_golden(path=None):
    p = Path(path) if path else (ROOT / "tests" / "rag_golden.json")
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def evaluate(golden, owner="", repo=""):
    """Calcula recall@k y MRR sobre un golden set."""
    if not golden:
        return {"error": "golden set vacío"}
    recalls = []
    mrrs = []
    for g in golden:
        q = g["q"]
        exp_src = g.get("expected_source")
        exp_path = g.get("expected_path")
        res = unified_retrieve(q, owner=owner, repo=repo, k=5, audit=False)
        hit_rank = None
        for i, r in enumerate(res, start=1):
            if (exp_src and r["source"].startswith(exp_src)) or (exp_path and exp_path in r["path"]):
                hit_rank = i
                break
        recalls.append(1.0 if hit_rank else 0.0)
        mrrs.append(1.0 / hit_rank if hit_rank else 0.0)
    n = len(golden)
    return {
        "n": n,
        "recall_at_5": round(sum(recalls) / n, 3),
        "mrr": round(sum(mrrs) / n, 3),
        "by_source": provenance_summary([r for g in golden for r in unified_retrieve(g["q"], owner=owner, repo=repo, k=5, audit=False)]),
    }


AUDIT_FILE = ROOT / "memory" / "rag_audit.jsonl"


def _audit(query, owner, repo, results):
    try:
        AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": time.time(),
            "query": query,
            "owner": owner,
            "repo": repo,
            "n_results": len(results),
            "results": [{"source": r.get("source"), "path": r.get("path"), "score": r.get("score")} for r in results],
        }
        with AUDIT_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def read_audit(limit=50):
    if not AUDIT_FILE.exists():
        return []
    lines = AUDIT_FILE.read_text(encoding="utf-8").splitlines()
    out = []
    for ln in lines[-limit:]:
        try:
            out.append(json.loads(ln))
        except Exception:
            pass
    return out


def audit_stats():
    entries = read_audit(limit=10000)
    from collections import Counter
    src_counter = Counter()
    for e in entries:
        for r in e.get("results", []):
            src_counter[r.get("source", "?").split(":")[0]] += 1
    return {
        "total_queries": len(entries),
        "results_by_source": dict(src_counter),
        "last_query": entries[-1].get("query") if entries else None,
    }
