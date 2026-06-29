"""
reranker.py — re-scores retrieved chunks using a cross-encoder.

WHAT'S THE DIFFERENCE FROM YOUR EXISTING EMBEDDING MODEL?
-------------------------------------------------------------
Your embeddings.py model (all-MiniLM-L6-v2) is a "bi-encoder": it
looks at the question and a chunk SEPARATELY, turns each into a
vector, then measures distance between the two vectors. This is fast
because chunks only need to be embedded ONCE (when uploaded) and
reused for every future question.

A cross-encoder is different: it looks at the question AND a chunk
TOGETHER, as one combined input, and directly outputs a relevance
score (0 to 1, roughly "how relevant is this chunk to this exact
question"). It's much more accurate because it can actually compare
the two pieces of text directly - but it's slower, since nothing can
be pre-computed in advance.

THE STRATEGY: use both, in two stages.
    Stage 1 (vector search, already built) - fast, casts a wide net,
             pulls e.g. top 15 candidates out of possibly thousands
             of chunks.
    Stage 2 (re-ranking, this file) - slow but accurate, only has to
             score those 15 candidates, then keeps the best few.

This combo gives you speed AND accuracy, instead of picking one.

MODEL USED:
    cross-encoder/ms-marco-MiniLM-L-6-v2
    A small, fast cross-encoder trained specifically for "is this
    passage relevant to this query" - exactly our use case.

Install (if not already present):
    pip install sentence-transformers
"""

from sentence_transformers import CrossEncoder

# Loaded once when the server starts (not per-request) - loading a
# model from disk/downloading it is slow, so we want this done ONCE
# and reused for every chat request afterward.
_reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(question: str, candidates: list[dict], top_n: int = 4):
    """
    Takes the candidates already found by vector search and re-orders
    them by actual relevance to the question, keeping only the best
    top_n.

    candidates: list of dicts like
        {"source": ..., "chunk": ..., "content": ...}
        (this is exactly the shape retrieve_context() already builds)

    Returns: the same list, re-ordered and trimmed to top_n.
    """
    if not candidates:
        return []

    # Cross-encoders expect pairs: [(question, chunk_text), (question, chunk_text), ...]
    pairs = [(question, c["content"]) for c in candidates]

    # .predict() runs the model on every pair and returns a relevance
    # score for each one - higher score = more relevant
    scores = _reranker.predict(pairs)

    print(f"[reranker] scored {len(candidates)} candidates: "
          f"{[round(float(s), 3) for s in scores]}")

    # attach scores so we can sort, then drop the score before returning
    # (the rest of the app doesn't need to know about it)
    scored = list(zip(candidates, scores))
    scored.sort(key=lambda pair: pair[1], reverse=True)  # highest score first

    top_candidates = [item for item, score in scored[:top_n]]

    print(f"[reranker] kept top {len(top_candidates)} after re-ranking")

    return top_candidates