from fastembed import TextEmbedding

# same model as before — fastembed supports all-MiniLM-L6-v2 natively
_model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")


def get_embedding(text: str) -> list[float]:
    # fastembed.embed() returns a generator of numpy arrays, one per
    # input text. We pass one string so we get one result back.
    # list(...)[0] pulls the first (only) result, .tolist() converts
    # the numpy array into a plain Python list that ChromaDB expects.
    embeddings = list(_model.embed([text]))
    return embeddings[0].tolist()