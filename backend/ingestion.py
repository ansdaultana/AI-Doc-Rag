from pdf_utils import extract_text_from_pdf  # PDF → text
from chunking import chunk_text  # text → chunks
from embeddings import get_embedding  # text → vector
from vector_store import add_chunks  # store vectors


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
