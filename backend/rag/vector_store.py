import chromadb  # vector database

client = chromadb.PersistentClient(path="./chroma_db")  # persistent storage

# IMPORTANT: explicitly set the distance metric.
# Chroma's default is "l2" (squared L2), NOT cosine.
# all-MiniLM-L6-v2 embeddings are near-unit-norm, so cosine distance
# (range ~0-2, "similar" close to 0) behaves much more predictably
# with a fixed threshold like 0.85 than raw L2 does.
collection = client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}
)  # document collection


def add_chunks(chunks, embeddings, doc_name: str):
    ids = [
        f"{doc_name}_chunk_{i}"
        for i in range(len(chunks))
    ]  # generate unique chunk ids

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=[
            {
                "doc": doc_name,
                "chunk_index": i
            }
            for i in range(len(chunks))
        ]
    )

    # DEBUG: confirm what actually landed in the collection
    print(f"[vector_store] added {len(chunks)} chunks for doc='{doc_name}'")
    print(f"[vector_store] collection now has {collection.count()} total chunks")


def search_chunks(
    query_embedding,
    top_k=15,  # widened from 8: the re-ranker (stage 2) needs a bigger
               # pool of candidates to actually choose the best ones
               # from - too narrow a net here defeats the point of
               # adding re-ranking at all.
    doc_name=None
):
    if doc_name:
        print(f"[vector_store] searching with FILTER doc='{doc_name}'")
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"doc": doc_name},
            include=["documents", "metadatas", "distances"]
        )
    else:
        print("[vector_store] searching with NO doc filter")
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

    # DEBUG: show raw hit count + distance range before any thresholding happens
    n_hits = len(results["documents"][0]) if results["documents"] else 0
    print(f"[vector_store] raw hits returned: {n_hits}")
    if n_hits:
        print(f"[vector_store] distances: {results['distances'][0]}")
    else:
        print("[vector_store] NOTE: 0 hits means either the collection is "
              "empty, the doc_name filter matched nothing, or top_k=0.")

    return results


def get_documents():
    data = collection.get(
        include=["metadatas"]
    )

    docs = set()

    for meta in data["metadatas"]:
        docs.add(meta["doc"])

    return list(docs)


def debug_dump_collection():
    """
    Call this manually (e.g. in a python shell or a temp /debug route)
    to sanity-check what's actually stored, independent of any query.
    """
    count = collection.count()
    print(f"[debug] total chunks in collection: {count}")
    if count == 0:
        print("[debug] collection is EMPTY - ingestion never wrote anything, "
              "or you're pointed at a different ./chroma_db path than you "
              "think (check your working directory when you run uvicorn).")
        return
    sample = collection.get(limit=3, include=["documents", "metadatas"])
    for doc, meta in zip(sample["documents"], sample["metadatas"]):
        print(f"[debug] doc='{meta.get('doc')}' chunk_index={meta.get('chunk_index')} "
              f"preview={doc[:80]!r}")