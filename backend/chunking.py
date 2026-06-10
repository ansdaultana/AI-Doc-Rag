def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    chunks = []  # stores all chunks

    start = 0

    while start < len(text):
        end = start + chunk_size  # define chunk boundary

        chunks.append(text[start:end])  # add chunk

        start = end - overlap  # maintain overlap

    return chunks  # return chunk list
