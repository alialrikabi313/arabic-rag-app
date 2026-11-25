# -*- coding: utf-8 -*-
"""اختبارات الخلفية على فهرس حقيقي مبني من عيّنة ويكيبيديا (بلا بيانات مخترَعة).

الحالات: سؤال ولّده نموذج على مقالة «الرعاية الملائمة في وقت مبكر» (مرحلة 3 من
arabic-rag-bench)، وسؤال خارج النطاق (منسف) سجّل 0.39 في المعايرة. تُتخطّى إن غاب الفهرس.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import CHUNKS_DB, EMBEDDINGS_NPY
from server import NOT_FOUND_ANSWER, build_messages, create_app

_REAL_Q = "في أي عام تم اقتراح مصطلح الرعاية الملائمة في وقت مبكر لأول مرة؟"
_OOD_Q = "كيف أطبخ المنسف الأردني؟"


@pytest.fixture(scope="module")
def retriever():
    if not (CHUNKS_DB.exists() and EMBEDDINGS_NPY.exists()):
        pytest.skip("الفهرس غير مبني (شغّل build_index.py)")
    from retriever import Retriever

    return Retriever.load()


def _client(retriever, calls: list):
    def fake_generate(messages):
        calls.append(messages)
        return "اقتُرح المصطلح عام 2013 [1]."

    return TestClient(create_app(retriever, fake_generate))


def test_real_question_returns_source_and_calls_llm_with_numbered_sources(retriever):
    calls: list = []
    body = _client(retriever, calls).post("/ask", json={"question": _REAL_Q}).json()
    assert body["sources"][0]["title"] == "الرعاية الملائمة في وقت مبكر"
    assert body["answer"].startswith("اقتُرح")
    assert "[1] الرعاية الملائمة في وقت مبكر" in calls[0][1]["content"]


def test_out_of_domain_question_refuses_without_calling_llm(retriever):
    calls: list = []
    body = _client(retriever, calls).post("/ask", json={"question": _OOD_Q}).json()
    assert body == {"answer": NOT_FOUND_ANSWER, "sources": []}
    assert calls == []


def test_empty_question_is_rejected_by_validation(retriever):
    assert _client(retriever, []).post("/ask", json={"question": ""}).status_code == 422


def test_build_messages_numbers_sources_from_one():
    from retriever import Hit

    hits = [Hit("أ", "u1", "نص أول", 0.9), Hit("ب", "u2", "نص ثانٍ", 0.8)]
    user = build_messages("س؟", hits)[1]["content"]
    assert user.index("[1] أ") < user.index("[2] ب") < user.index("السؤال: س؟")
