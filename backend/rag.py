from embeddings import get_embedding  # question embedding
from vector_store import search_chunks  # vector search


def retrieve_context(question: str):
    query_embedding = get_embedding(question)  # embed question

    results = search_chunks(query_embedding)  # retrieve chunks

    chunks = results["documents"][0]

    metadata = results["metadatas"][0]

    context_items = []

    for i in range(len(chunks)):
        meta = metadata[i] or {}  # safe metadata handling

        context_items.append({
            "source": meta.get("doc", "unknown"),
            "content": chunks[i]
        })

    return context_items  # structured retrieval output
