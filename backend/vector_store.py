import chromadb  # vector database


client = chromadb.PersistentClient(path="./chroma_db")  # persistent storage

collection = client.get_or_create_collection(
    name="documents"
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
            {"doc": doc_name}
            for _ in chunks
        ]
    )  # store chunks and metadata


def search_chunks(query_embedding, top_k=3):
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas"]
    )  # retrieve relevant chunks
