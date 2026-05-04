"""Lightweight RAG: load frontmatter-markdown chunks, metadata filter, lexical score."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from app.config import get_settings


@dataclass
class RagChunk:
    source: str
    topic: str
    body: str
    meta: dict


def _split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        meta = {}
    return meta, parts[2].strip()


def _score(query: str, body: str) -> float:
    q = set(re.findall(r"[a-zA-Z0-9_]+", query.lower()))
    b = set(re.findall(r"[a-zA-Z0-9_]+", body.lower()))
    if not q:
        return 0.0
    return len(q & b) / len(q)


class RagEngine:
    def __init__(self, data_dir: str | None = None) -> None:
        self.chunks: list[RagChunk] = []
        root = Path(__file__).resolve().parents[3]
        d = Path(data_dir or get_settings().rag_data_dir)
        if not d.is_absolute():
            d = root / d
        self._load_dir(d)

    def _load_dir(self, d: Path) -> None:
        if not d.exists():
            return
        for p in d.rglob("*.md"):
            raw = p.read_text(encoding="utf-8", errors="ignore")
            meta, body = _split_frontmatter(raw)
            self.chunks.append(
                RagChunk(
                    source=str(meta.get("source", p.name)),
                    topic=str(meta.get("topic", "")),
                    body=body,
                    meta=meta,
                )
            )

    def query(
        self,
        q: str,
        *,
        circuit_type: str | None = None,
        topic: str | None = None,
        max_results: int = 5,
    ) -> list[dict]:
        out: list[tuple[float, RagChunk]] = []
        for c in self.chunks:
            if circuit_type and c.meta.get("circuit_type") and c.meta.get("circuit_type") != circuit_type:
                continue
            if topic and topic.lower() not in (c.topic + c.body).lower():
                continue
            s = _score(q, c.topic + "\n" + c.body)
            out.append((s, c))
        out.sort(key=lambda x: x[0], reverse=True)
        results = []
        for s, c in out[:max_results]:
            if s == 0 and q:
                continue
            results.append(
                {
                    "score": round(s, 4),
                    "source": c.source,
                    "topic": c.topic,
                    "snippet": c.body[:1200],
                    "meta": {k: v for k, v in c.meta.items() if k not in ("source", "topic")},
                }
            )
        if not results and self.chunks:
            # fallback: top lexical without filters
            out = sorted((( _score(q, c.topic + c.body), c) for c in self.chunks), reverse=True)
            for s, c in out[:max_results]:
                results.append(
                    {
                        "score": round(s, 4),
                        "source": c.source,
                        "topic": c.topic,
                        "snippet": c.body[:1200],
                        "meta": c.meta,
                    }
                )
        return results
