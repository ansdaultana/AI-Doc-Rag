from fastembed import TextEmbedding

_model = None

def get_embedding(text: str) -> list[float]:
    global _model
    if _model is None:
        _model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    embeddings = list(_model.embed([text]))
    return embeddings[0].tolist()