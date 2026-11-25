# -*- coding: utf-8 -*-
"""بناء الفهرس: تقطيع المقالات بالفقرات وتضمينها.

يقرأ: SOURCE_JSONL (سطر لكل مقالة: pageid, title, url, text).
ينتج: chunks.sqlite و chunk_embeddings.npy في INDEX_DIR.
"""

import json
import re
import sqlite3
import sys

import numpy as np

from config import (
    CHUNKS_DB,
    EMBED_BATCH,
    EMBED_DEVICE,
    EMBED_MODEL,
    EMBEDDINGS_NPY,
    INDEX_DIR,
    MAX_CHUNK_WORDS,
    SOURCE_JSONL,
)

# عناوين ويكيبيديا النصّية: == عنوان ==
_HEADING_RE = re.compile(r"^=+\s*.+?\s*=+$")


def paragraph_chunks(text: str) -> list[str]:
    # الفقرة وحدة طبيعية؛ تُدمج الصغيرة حتى MAX، والفقرة الأطول من MAX تبقى كما هي
    paras = [p.strip() for p in text.split("\n") if p.strip() and not _HEADING_RE.match(p.strip())]
    chunks: list[str] = []
    cur: list[str] = []
    cur_words = 0
    for p in paras:
        w = len(p.split())
        if cur and cur_words + w > MAX_CHUNK_WORDS:
            chunks.append(" ".join(cur))
            cur, cur_words = [], 0
        cur.append(p)
        cur_words += w
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def main() -> None:
    if not SOURCE_JSONL.exists():
        sys.exit(f"لا يوجد مصدر: {SOURCE_JSONL} (ولّده بـ arabic-rag-bench/01_fetch_sample.py)")

    # استيراد كسول: المكتبة ثقيلة ولا حاجة لها قبل هذه النقطة
    from sentence_transformers import SentenceTransformer

    with SOURCE_JSONL.open(encoding="utf-8") as f:
        articles = [json.loads(line) for line in f]

    rows = [
        (a["pageid"], a["title"], a["url"], i, chunk)
        for a in articles
        for i, chunk in enumerate(paragraph_chunks(a["text"]))
    ]
    print(f"◄ {len(articles)} مقالة ← {len(rows)} مقطع")

    model = SentenceTransformer(EMBED_MODEL, device=EMBED_DEVICE)
    vecs = model.encode([r[4] for r in rows], batch_size=EMBED_BATCH, normalize_embeddings=True)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    np.save(EMBEDDINGS_NPY, vecs.astype(np.float32))
    CHUNKS_DB.unlink(missing_ok=True)
    con = sqlite3.connect(CHUNKS_DB)
    con.executescript(
        """
        CREATE TABLE chunks (
            row_id INTEGER PRIMARY KEY,
            pageid INTEGER NOT NULL,
            title  TEXT NOT NULL,
            url    TEXT NOT NULL,
            chunk_no INTEGER NOT NULL,
            text   TEXT NOT NULL
        );
        """
    )
    con.executemany(
        "INSERT INTO chunks VALUES (?,?,?,?,?,?)",
        [(i, *r) for i, r in enumerate(rows)],
    )
    con.commit()
    con.close()
    print(f"✓ {CHUNKS_DB.name} + {EMBEDDINGS_NPY.name} {vecs.shape}")


if __name__ == "__main__":
    main()
