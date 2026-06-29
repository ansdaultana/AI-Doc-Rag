# RAG Pipeline — Variable Reference

A quick lookup for what each major variable looks like as data flows
through the retrieval → re-ranking → LLM pipeline. All examples use
the same running case: question = **"who is ans nazir"**, searched
against `who_is_ans_nazir.pdf`.

---

## `rag.py`

### `query_embedding`
The question, turned into a vector (list of numbers) by the embedding model.
```python
query_embedding = [0.0123, -0.0456, 0.0891, ...]   # 384 numbers total
```

### `results`
Raw output from ChromaDB's `.query()`. A dictionary of **lists of lists**
— the outer list always has exactly one inner list (one per question searched).
```python
results = {
    "documents": [[
        "Ans Nazir is a Computer Science graduate...",
        "Ans currently works at i2c...",
        "Family relationships. Love. Life choices...",
    ]],
    "metadatas": [[
        {"doc": "who_is_ans_nazir.pdf", "chunk_index": 0},
        {"doc": "who_is_ans_nazir.pdf", "chunk_index": 1},
        {"doc": "who_is_ans_nazir.pdf", "chunk_index": 4},
    ]],
    "distances": [[0.43, 0.76, 0.89]]
}
```

### `chunks`, `metadata`, `distances`
The three inner lists, unpacked for easier use.
```python
chunks = results["documents"][0]
metadata = results["metadatas"][0]
distances = results["distances"][0]
```

### `candidates`
Built by looping over `chunks`/`metadata`/`distances` together, keeping
only entries under the distance threshold (0.85), reshaped into one
dict per chunk.
```python
candidates = [
    {"source": "who_is_ans_nazir.pdf", "chunk": 0, "content": "Ans Nazir is a Computer Science graduate..."},
    {"source": "who_is_ans_nazir.pdf", "chunk": 1, "content": "Ans currently works at i2c..."},
    {"source": "who_is_ans_nazir.pdf", "chunk": 4, "content": "Family relationships. Love. Life choices..."},
]
```

### `final_context` (returned by `rerank()`)
The cross-encoder re-scores each candidate against the actual question
and keeps only the top N (default 4). Order is now by **relevance**,
not by original position in the document.
```python
final_context = [
    {"source": "who_is_ans_nazir.pdf", "chunk": 0, "content": "Ans Nazir is a Computer Science graduate..."},
    {"source": "who_is_ans_nazir.pdf", "chunk": 1, "content": "Ans currently works at i2c..."},
]
# chunk 4 (about movies) scored low for relevance and got dropped
```

---

## `reranker.py`

### `pairs`
The candidates paired with the question, in the exact shape the
cross-encoder model expects.
```python
pairs = [
    ("who is ans nazir", "Ans Nazir is a Computer Science graduate..."),
    ("who is ans nazir", "Ans currently works at i2c..."),
    ("who is ans nazir", "Family relationships. Love. Life choices..."),
]
```

### `scores`
One relevance score per pair, in the same order. Higher = more relevant.
```python
scores = [0.92, 0.81, 0.06]
```

### `scored`
`candidates` and `scores` glued together by position using `zip()`,
then sorted highest-score-first.
```python
scored = [
    ({"source": ..., "content": "Ans Nazir is a CS graduate..."}, 0.92),
    ({"source": ..., "content": "Ans currently works at i2c..."}, 0.81),
    ({"source": ..., "content": "Family relationships..."}, 0.06),
]
```

---

## `main.py`

### `context_items`
Just `final_context`, received under this name inside the `/chat` route.
Same data as `final_context` above.

### `context_text`
All chunks in `context_items`, joined into one readable string for the LLM prompt.
```python
context_text = """Source: who_is_ans_nazir.pdf
Content: Ans Nazir is a Computer Science graduate...

Source: who_is_ans_nazir.pdf
Content: Ans currently works at i2c..."""
```

### `sources_list`
Just the filenames from `context_items`, deduplicated (no repeats even
if multiple chunks came from the same file).
```python
sources_list = ["who_is_ans_nazir.pdf"]
```

### `history_rows`
This session's last 6 messages, pulled from Postgres (`messages` table),
oldest-first. Each item is a database row object, not a plain dict —
access fields with `.role`, `.content`, not `["role"]`.
```python
history_rows = [
    Message(role="user", content="where does he work"),
    Message(role="assistant", content="Ans works at i2c..."),
]
```

### `messages`
The full payload sent to the Groq LLM: system prompt + recent history
+ the new question wrapped with its retrieved context.
```python
messages = [
    {"role": "system", "content": "You are a documentation assistant..."},
    {"role": "user", "content": "where does he work"},
    {"role": "assistant", "content": "Ans works at i2c..."},
    {"role": "user", "content": "Context:\nSource: who_is_ans_nazir.pdf\nContent: Ans Nazir is a CS graduate...\n\nQuestion:\nwho is ans nazir"}
]
```

### `assistant_response`
The plain text answer returned by the LLM.
```python
assistant_response = "Ans Nazir is a Computer Science graduate from Information Technology University..."
```

---

## One-line map of the whole journey

```
question
  → query_embedding          (question as a vector)
  → results                  (raw ChromaDB match data)
  → chunks / metadata / distances   (unpacked from results)
  → candidates                (filtered by distance threshold)
  → pairs → scores → scored   (re-ranking stage)
  → final_context / context_items   (re-ranked, trimmed to top N)
  → context_text              (formatted into one string)
  → messages                  (full LLM prompt, history + context + question)
  → assistant_response        (the AI's answer)
```