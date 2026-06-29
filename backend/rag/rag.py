from rag.embeddings import get_embedding
from rag.vector_store import search_chunks
from rag.reranker import rerank

# Threshold meaning now matches cosine DISTANCE (0 = identical, 2 = opposite).
# 0.85 was likely tuned assuming cosine distance already - this becomes
# correct once vector_store.py sets hnsw:space="cosine". If you were
# previously on the default l2 space, raw distances could easily have
# been >0.85 even for great matches, silently nuking everything.
DISTANCE_THRESHOLD = 0.85

# How many chunks to keep after re-ranking - this is the FINAL number
# of chunks that actually get sent to the LLM as context.
FINAL_TOP_N = 4


def retrieve_context(
    question: str,
    doc_name: str = None
):
    query_embedding = get_embedding(question)  # embed question

    # STAGE 1: fast vector search - cast a WIDE net here. We want more
    # raw candidates than before (top_k is set in vector_store.py),
    # because the re-ranker (stage 2) needs a decent pool to choose
    # from. Picking too few here defeats the point of re-ranking.
    results = search_chunks(
        query_embedding,
        doc_name=doc_name
    )

    if not results["documents"] or not results["documents"][0]:
        print("[rag] no documents returned from search_chunks at all "
              "(empty collection, bad filter, or top_k=0)")
        return []

    chunks = results["documents"][0]
    metadata = results["metadatas"][0]
    distances = results["distances"][0]

    candidates = []
    kept = 0
    skipped = 0

    for i in range(len(chunks)):
        meta = metadata[i] or {}

        if distances[i] > DISTANCE_THRESHOLD:
            skipped += 1
            print(f"[rag] SKIP chunk {i} (doc={meta.get('doc')}, "
                  f"chunk_index={meta.get('chunk_index')}) "
                  f"distance={distances[i]:.4f} > {DISTANCE_THRESHOLD}")
            continue

        kept += 1
        candidates.append({
            "source": meta.get("doc", "unknown"),
            "chunk": meta.get("chunk_index", -1),
            "content": chunks[i]
        })
        
        
    print(f"[rag] stage 1 (vector search): kept {kept} / skipped {skipped} "
          f"(threshold={DISTANCE_THRESHOLD})")

    if not candidates:
        print("[rag] WARNING: every candidate was filtered out by the "
              "distance threshold. If 'raw hits returned' above was > 0, "
              "the bug is the threshold/metric, not retrieval itself.")
        return []

    # STAGE 2: re-rank the surviving candidates with the cross-encoder,
    # keeping only the FINAL_TOP_N most genuinely relevant ones.
    final_context = rerank(question, candidates, top_n=FINAL_TOP_N)

    print(f"[rag] stage 2 (re-ranking): {len(candidates)} candidates "
          f"-> {len(final_context)} final chunks sent to the LLM")

    return final_context