from embeddings import get_embedding  # question embedding
from vector_store import search_chunks  # vector search

# Threshold meaning now matches cosine DISTANCE (0 = identical, 2 = opposite).
# 0.85 was likely tuned assuming cosine distance already - this becomes
# correct once vector_store.py sets hnsw:space="cosine". If you were
# previously on the default l2 space, raw distances could easily have
# been >0.85 even for great matches, silently nuking everything.
DISTANCE_THRESHOLD = 0.85


def retrieve_context(
    question: str,
    doc_name: str = None
):
    query_embedding = get_embedding(question)  # embed question

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

    context_items = []
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
        context_items.append({
            "source": meta.get("doc", "unknown"),
            "chunk": meta.get("chunk_index", -1),
            "content": chunks[i]
        })

    print(f"[rag] kept {kept} / skipped {skipped} (threshold={DISTANCE_THRESHOLD})")

    if not context_items:
        print("[rag] WARNING: every candidate was filtered out by the "
              "distance threshold. If 'raw hits returned' above was > 0, "
              "the bug is the threshold/metric, not retrieval itself.")

    return context_items