"""
Token-based chunking.

WHY THIS EXISTS (read this if you're learning):
-------------------------------------------------
The old version split text every N *characters*. That's like cutting a
cake every 2 inches regardless of where the slices of frosting are - you
might cut straight through a decoration. Characters don't know where
sentences end.

This version does two things differently:

1. It measures chunk size in TOKENS, not characters. A token is roughly
   a word-piece - the actual unit the embedding model and the LLM think
   in. Using tokens means your chunk size setting (e.g. 500) means the
   same thing every time, regardless of whether the text is dense
   technical jargon or simple prose.

2. It uses LangChain's RecursiveCharacterTextSplitter, which tries to
   cut at natural boundaries FIRST (paragraph breaks, then sentences,
   then words) and only falls back to a hard cut as a last resort. So
   chunks stay semantically coherent much more often.

Install what this needs:
    pip install langchain-text-splitters tiktoken
"""

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

# tiktoken's cl100k_base encoding is a good general-purpose tokenizer -
# it's the same family used by many modern LLMs, so token counts here
# will be close to what your embedding model / LLM actually sees.
_encoding = tiktoken.get_encoding("cl100k_base")


def _count_tokens(text: str) -> int:
    """Tells the splitter how many tokens a piece of text is, instead
    of how many characters - this is what makes chunk_size 'token-based'."""
    return len(_encoding.encode(text))


def chunk_text(
    text: str,
    chunk_size: int = 500,   # now means 500 TOKENS, not 500 characters
    chunk_overlap: int = 50  # 50 tokens of overlap between consecutive chunks
):
    """
    Splits a document into overlapping, token-sized chunks that try to
    respect sentence/paragraph boundaries.

    chunk_overlap exists so context isn't lost at chunk edges - e.g. if
    a sentence explaining something starts in chunk 2 and the answer is
    in chunk 3, a bit of overlap means each chunk still has some
    surrounding context, not just a clean break with nothing on either side.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=_count_tokens,  # <-- the key change: measure in tokens
        separators=[
            "\n\n",  # paragraph breaks - try this first
            "\n",    # then line breaks
            ". ",    # then sentence ends
            " ",     # then just words
            ""       # absolute last resort: characters
        ],
    )

    chunks = splitter.split_text(text)

    print(f"[chunking] split into {len(chunks)} chunks "
          f"(target size={chunk_size} tokens, overlap={chunk_overlap} tokens)")

    return chunks