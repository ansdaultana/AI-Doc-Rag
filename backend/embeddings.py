from sentence_transformers import SentenceTransformer  # text embedding model


model = SentenceTransformer("all-MiniLM-L6-v2")  # lightweight embedding model


def get_embedding(text: str):
    return model.encode(text).tolist()  # convert text to vector
