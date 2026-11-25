# -*- coding: utf-8 -*-
"""خلفية RAG: POST /ask يبحث في الفهرس ثم يولّد إجابة من المقاطع المسترجَعة مع مصادرها.

التشغيل: python server.py (يتطلب فهرساً مبنياً بـ build_index.py ونموذجاً على Ollama).
"""

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import LLM_MODEL, LLM_TIMEOUT_SEC, MIN_SCORE, OLLAMA_URL, TOP_K
from retriever import Hit, Retriever

NOT_FOUND_ANSWER = "لم أجد في المقالات المتاحة ما يجيب عن هذا السؤال."

_SYSTEM = (
    "أجب عن السؤال بالعربية الفصحى وبإيجاز، اعتماداً على المصادر المرقّمة فقط. "
    "اذكر رقم المصدر بين قوسين مثل [1] بعد كل معلومة. "
    "إن لم تجد الجواب في المصادر فقل ذلك صراحةً ولا تخترع."
)


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


def build_messages(question: str, hits: list[Hit]) -> list[dict]:
    sources = "\n\n".join(f"[{i}] {h.title}\n{h.text}" for i, h in enumerate(hits, 1))
    return [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": f"المصادر:\n{sources}\n\nالسؤال: {question}"},
    ]


def ollama_generate(messages: list[dict]) -> str:
    body = {"model": LLM_MODEL, "messages": messages, "stream": False, "think": False,
            "options": {"temperature": 0.2}}
    try:
        resp = httpx.post(OLLAMA_URL, json=body, timeout=LLM_TIMEOUT_SEC)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(503, f"نموذج اللغة غير متاح: {type(e).__name__}") from e
    return resp.json()["message"]["content"].strip()


def create_app(retriever: Retriever, generate=ollama_generate) -> FastAPI:
    app = FastAPI(title="arabic-rag-app backend")
    # CORS مفتوح: للتطوير المحلي فقط (واجهة Flutter web على منفذ آخر). قيّده قبل أي نشر عام
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.post("/ask")
    def ask(req: AskRequest) -> dict:
        hits = retriever.search(req.question, TOP_K)
        if not hits or hits[0].score < MIN_SCORE:
            return {"answer": NOT_FOUND_ANSWER, "sources": []}
        answer = generate(build_messages(req.question, hits))
        sources = [
            {"title": h.title, "url": h.url, "snippet": h.snippet, "score": round(h.score, 3)}
            for h in hits
        ]
        return {"answer": answer, "sources": sources}

    return app


def main() -> None:
    import uvicorn

    uvicorn.run(create_app(Retriever.load()), host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
