# -*- coding: utf-8 -*-
"""البحث: تضمين السؤال ومقارنته بكل المقاطع بجداء داخلي (cosine لأن التضمين مطبَّع)."""

import sqlite3
from dataclasses import dataclass

import numpy as np

from config import (
    CHUNKS_DB,
    EMBED_DEVICE,
    EMBED_MODEL,
    EMBEDDINGS_NPY,
    SNIPPET_CHARS,
)


@dataclass(frozen=True)
class Hit:
    title: str
    url: str
    text: str
    score: float

    @property
    def snippet(self) -> str:
        return self.text if len(self.text) <= SNIPPET_CHARS else self.text[:SNIPPET_CHARS].rstrip() + "…"


class Retriever:
    def __init__(self, embed, vecs: np.ndarray, rows: list[tuple[str, str, str]]) -> None:
        # embed: دالة نص ← متجه مطبَّع (تُحقن كي تُختبر المنطق بلا نموذج ثقيل)
        self._embed = embed
        self._vecs = vecs
        self._rows = rows

    @classmethod
    def load(cls) -> "Retriever":
        # استيراد كسول: المكتبة ثقيلة
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(EMBED_MODEL, device=EMBED_DEVICE)
        vecs = np.load(EMBEDDINGS_NPY)
        con = sqlite3.connect(CHUNKS_DB)
        rows = con.execute("SELECT title, url, text FROM chunks ORDER BY row_id").fetchall()
        con.close()
        return cls(lambda q: model.encode(q, normalize_embeddings=True), vecs, rows)

    def search(self, question: str, k: int) -> list[Hit]:
        q = self._embed(question)
        scores = self._vecs @ q
        top = np.argsort(-scores)[:k]
        return [Hit(*self._rows[i], float(scores[i])) for i in top]
