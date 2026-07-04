"""
reranker.py — re-scores retrieved chunks using fastembed's reranker.

"""

from fastembed.rerank.cross_encoder import TextCrossEncoder

# cross-encoder model for reranking — same concept as before:
# takes (question, chunk) pairs and scores their relevance together
_reranker = TextCrossEncoder(
    model_name="Xenova/ms-marco-MiniLM-L-6-v2"
)


def rerank(question: str, candidates: list[dict], top_n: int = 4):
    """
    Re-scores candidates by actual relevance to the question.
    Returns the top_n most relevant, highest score first.
    """
    if not candidates:
        return []

    passages = [c["content"] for c in candidates]

    # returns scores as a generator, one per passage
    scores = list(_reranker.rerank(question, passages))

    print(f"[reranker] scored {len(candidates)} candidates: "
          f"{[round(float(s), 3) for s in scores]}")

    scored = list(zip(candidates, scores))
    scored.sort(key=lambda pair: pair[1], reverse=True)

    top_candidates = [item for item, score in scored[:top_n]]

    print(f"[reranker] kept top {len(top_candidates)} after re-ranking")

    return top_candidates