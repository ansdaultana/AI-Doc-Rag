from fastembed.rerank.cross_encoder import TextCrossEncoder

_reranker = None

def rerank(question: str, candidates: list[dict], top_n: int = 4):
    global _reranker
    if _reranker is None:
        _reranker = TextCrossEncoder(model_name="Xenova/ms-marco-MiniLM-L-6-v2")

    if not candidates:
        return []

    passages = [c["content"] for c in candidates]
    scores = list(_reranker.rerank(question, passages))

    scored = list(zip(candidates, scores))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    top_candidates = [item for item, score in scored[:top_n]]

    print(f"[reranker] kept top {len(top_candidates)} after re-ranking")
    return top_candidates
