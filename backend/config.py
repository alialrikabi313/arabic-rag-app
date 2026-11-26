# -*- coding: utf-8 -*-
"""إعدادات الخلفية. عدّل هنا فقط عند تغيير المصدر أو النموذج أو العتبات."""

import os
from pathlib import Path

_HERE = Path(__file__).resolve().parent

# JSONL بصيغة arabic-rag-bench: سطر لكل مقالة (pageid, title, url, text)
SOURCE_JSONL = Path(
    os.environ.get("RAG_SOURCE_JSONL", _HERE.parent.parent / "arabic-rag-bench-data" / "wiki_sample_300.jsonl")
)

# الفهرس المبني خارج الريبو كي لا يدخل git
INDEX_DIR = Path(os.environ.get("RAG_INDEX_DIR", _HERE.parent.parent / "arabic-rag-app-data"))
CHUNKS_DB = INDEX_DIR / "chunks.sqlite"
EMBEDDINGS_NPY = INDEX_DIR / "chunk_embeddings.npy"

EMBED_MODEL = "BAAI/bge-m3"
EMBED_BATCH = 64
# None = اختيار تلقائي (cuda إن وُجد وإلا cpu)
EMBED_DEVICE = os.environ.get("RAG_DEVICE")

# تقطيع بالفقرات: تفوّق في arabic-rag-bench (Hit@1 0.838 مقابل 0.725 للدلالي)،
# وهو أرخص: لا تضمين إضافي وقت البناء
MAX_CHUNK_WORDS = 250

TOP_K = 4

# تحت هذه الدرجة (cosine) لا نجيب: الأفضل الاعتراف بعدم المعرفة من إجابة مختلَقة.
# معايَرة على 442 سؤالاً سليماً و20 سؤالاً خارج النطاق:
#   عتبة 0.45: تُجاب 97% من السليمة و70% من الغريبة
#   عتبة 0.50: تُجاب 93% من السليمة و25% من الغريبة   ← الحالية
#   عتبة 0.55: تُجاب 82% من السليمة و0% من الغريبة
# التشابه وحده لا يفصل بنظافة؛ المطالبة تأمر النموذج بالاعتراف بعدم المعرفة كحاجز ثانٍ.
# سياسة غموض مؤقتة بانتظار قرار المالك
MIN_SCORE = 0.50

SNIPPET_CHARS = 220

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
LLM_MODEL = os.environ.get("RAG_LLM_MODEL", "qwen3.8:27b")
LLM_TIMEOUT_SEC = 300
