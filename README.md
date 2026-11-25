# arabic-rag-app

An Arabic (RTL) question-answering app over Arabic Wikipedia: a **Flutter** chat UI backed by a small **FastAPI** RAG service that retrieves with `bge-m3`, answers with a local LLM (Ollama), and **cites its sources**.

```
Flutter app ──POST /ask──▶ FastAPI ──▶ bge-m3 retrieval (cosine, paragraph chunks)
     ▲                         │                    │
     └── answer + sources ◀────┴──── Ollama LLM ◀───┘   (refuses below a similarity threshold)
```

## Why it is built this way

- **Paragraph chunking**, not semantic: it won on Arabic Wikipedia in the companion benchmark [arabic-rag-bench](https://github.com/alialrikabi313/arabic-rag-bench) and costs no extra embedding pass at index time.
- **Refuses instead of guessing.** If the best chunk scores below `MIN_SCORE` the backend answers "not found" without calling the LLM. The threshold is calibrated, not guessed: 80 in-domain questions (median 0.63, min 0.40) vs. 6 off-topic ones (max 0.48). `0.50` separates all the off-topic ones but also refuses ~9% of valid questions — a deliberate, documented trade-off in `backend/config.py`.
- **Explicit UTF-8 decoding** in the app: `package:http` assumes latin1 when the response has no charset, which silently corrupts Arabic. A test pins this.

## Run

```bash
# 1. Backend (needs Ollama running with the model in config.py)
cd backend
pip install -r requirements.txt
python build_index.py     # reads RAG_SOURCE_JSONL (arabic-rag-bench format), writes the index outside the repo
python server.py          # http://127.0.0.1:8000

# 2. App
cd ../app
flutter run -d chrome --dart-define=API_URL=http://localhost:8000
# Android emulator: --dart-define=API_URL=http://10.0.2.2:8000
```

## Test

```bash
cd backend && pytest tests          # real index, stubbed LLM (no Ollama needed)
cd app && flutter test && flutter analyze
```

Backend tests use real cases from the benchmark (an LLM-generated question on the Wikipedia article «الرعاية الملائمة في وقت مبكر», and an off-topic question that scored 0.39).

## Measured

End-to-end on a laptop (RTX 5090 Laptop GPU box, 27B local model): ~90 s for the first grounded answer including model load; off-topic questions are refused in ~3 s. A smaller local model is the obvious lever for latency.

## Limits

- Corpus is a small random Wikipedia sample (see arabic-rag-bench), so many questions are legitimately unanswerable.
- CORS is wide open for local development; restrict it before any public deployment.
- No streaming yet: the app waits for the full answer.

Wikipedia text is CC BY-SA 4.0; no article text is stored in this repository.
