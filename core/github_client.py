# -*- coding: utf-8 -*-
"""Zero · Cliente de GitHub (REST API)."""
from __future__ import annotations
import base64
from . import http
from . import settings as S


API = "https://api.github.com"


def _headers():
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    t = S.get_token()
    if t:
        h["Authorization"] = f"Bearer {t}"
    return h


def get_user():
    return http.request("GET", f"{API}/user", headers=_headers())


def search_repos(q, per_page=10):
    return http.request("GET", f"{API}/search/repositories", headers=_headers(),
                        body=None) if False else http.request("GET", f"{API}/search/repositories?q={q}&per_page={per_page}", headers=_headers())


def get_repo(owner, repo):
    return http.request("GET", f"{API}/repos/{owner}/{repo}", headers=_headers())


def get_tree(owner, repo, branch=""):
    if not branch:
        r = get_repo(owner, repo)
        if not r.ok:
            return r
        branch = (r.data or {}).get("default_branch", "main")
    return http.request("GET", f"{API}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1", headers=_headers())


def get_file(owner, repo, path, ref=""):
    url = f"{API}/repos/{owner}/{repo}/contents/{path}"
    if ref:
        url += f"?ref={ref}"
    r = http.request("GET", url, headers=_headers())
    if r.ok and isinstance(r.data, dict) and r.data.get("content"):
        try:
            r.data["_decoded"] = base64.b64decode(r.data["content"]).decode("utf-8", "replace")
        except Exception:
            r.data["_decoded"] = ""
    return r


def list_issues(owner, repo, state="open", per_page=20):
    return http.request("GET", f"{API}/repos/{owner}/{repo}/issues?state={state}&per_page={per_page}", headers=_headers())


def list_commits(owner, repo, per_page=10):
    return http.request("GET", f"{API}/repos/{owner}/{repo}/commits?per_page={per_page}", headers=_headers())
