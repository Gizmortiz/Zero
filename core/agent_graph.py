# -*- coding: utf-8 -*-
"""Zero · Agente con LangGraph (plan → retrieve → respond)."""
from __future__ import annotations
from typing import TypedDict, List

try:
    from langgraph.graph import StateGraph, END
    _HAS_LG = True
except Exception:
    _HAS_LG = False

from . import settings as S, chat_engine, repo_rag


class AgentState(TypedDict):
    question: str
    repo_ctx: str
    rag_ctx: str
    answer: str
    owner: str
    repo: str
    index: object


def _node_retrieve(state):
    # build RAG index if not present
    idx = state.get("index")
    if idx is None and state.get("owner") and state.get("repo"):
        idx = repo_rag.build_index(state["owner"], state["repo"])
    rag = repo_rag.query(idx, state["question"]) if idx is not None else ""
    state["index"] = idx
    state["rag_ctx"] = rag
    return state


def _node_respond(state):
    ctx = state.get("repo_ctx", "")
    if state.get("rag_ctx"):
        ctx = ctx + "\n\n--- RAG ---\n" + state["rag_ctx"]
    ans = chat_engine.answer(state["question"], repo_ctx=ctx)
    state["answer"] = ans
    return state


def run(question, repo_ctx="", owner="", repo="", index=None):
    if not _HAS_LG:
        return chat_engine.answer(question, repo_ctx=repo_ctx)
    graph = StateGraph(AgentState)
    graph.add_node("retrieve", _node_retrieve)
    graph.add_node("respond", _node_respond)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "respond")
    graph.add_edge("respond", END)
    app = graph.compile()
    out = app.invoke({
        "question": question, "repo_ctx": repo_ctx, "rag_ctx": "",
        "answer": "", "owner": owner, "repo": repo, "index": index,
    })
    return out.get("answer", "")
