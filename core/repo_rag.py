# -*- coding: utf-8 -*-
"""Zero · RAG sobre repos usando LlamaIndex (persistente en disco)."""
from __future__ import annotations
import os
from pathlib import Path

try:
    from llama_index.core import Document, VectorStoreIndex, Settings, StorageContext, load_index_from_storage
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    _HAS_LI = True
except Exception:
    _HAS_LI = False

from . import github_client as GH

ROOT = Path(__file__).resolve().parent.parent
INDEX_DIR = ROOT / "database" / "rag_index"


def _index_path(owner, repo):
    safe = f"{owner}_{repo}".replace("/", "_")
    return INDEX_DIR / safe


def _embed_model():
    try:
        return HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    except Exception:
        return None


def build_index(owner, repo, max_files=30, force=False):
    if not _HAS_LI:
        return None
    ipath = _index_path(owner, repo)
    # Try load from disk
    if not force and ipath.exists() and (ipath / "docstore.json").exists():
        try:
            Settings.embed_model = _embed_model()
            storage = StorageContext.from_defaults(persist_dir=str(ipath))
            return load_index_from_storage(storage)
        except Exception:
            pass
    # Build fresh
    try:
        Settings.embed_model = _embed_model()
    except Exception:
        pass
    r = GH.get_tree(owner, repo)
    if not r.ok or not isinstance(r.data, dict):
        return None
    paths = [t["path"] for t in r.data.get("tree", []) if t.get("type") == "blob"]
    docs = []
    for p in paths[:max_files]:
        if not any(p.endswith(ext) for ext in (".md", ".py", ".ts", ".js", ".json", ".txt", ".yaml", ".yml", ".toml", ".rs", ".go", ".java")):
            continue
        fr = GH.get_file(owner, repo, p)
        if fr.ok and isinstance(fr.data, dict):
            content = fr.data.get("_decoded", "")
            if content and len(content) < 15000:
                docs.append(Document(text=content, metadata={"path": p}))
    if not docs:
        return None
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=64)
    nodes = splitter.get_nodes_from_documents(docs)
    index = VectorStoreIndex(nodes)
    # Persist
    try:
        ipath.mkdir(parents=True, exist_ok=True)
        index.storage_context.persist(persist_dir=str(ipath))
    except Exception:
        pass
    return index


def query(index, question, top_k=5):
    if index is None:
        return ""
    try:
        retriever = index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(question)
        out = []
        for n in nodes:
            meta = getattr(n, "metadata", {}) or {}
            path = meta.get("path", "")
            out.append(f"--- {path} ---\n{n.get_content()[:700]}")
        return "\n\n".join(out)
    except Exception as e:
        return f"[RAG error] {e}"
