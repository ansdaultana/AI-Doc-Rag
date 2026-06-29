from ingestion.pdf_utils import extract_text_from_pdf
from rag.chunking import chunk_text
from rag.embeddings import get_embedding
from rag.vector_store import add_chunks


def ingest_document(file_path: str, doc_name: str):
    text = extract_text_from_pdf(file_path)  # extract PDF text

    chunks = chunk_text(text)  # split text

    embeddings = [
        get_embedding(chunk)
        for chunk in chunks
    ]  # generate chunk embeddings

    add_chunks(
        chunks,
        embeddings,
        doc_name
    )  # store in Chroma

    return len(chunks)  # return indexed chunk count
