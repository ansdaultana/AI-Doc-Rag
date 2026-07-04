from fastapi import FastAPI, UploadFile, File, Depends  # FastAPI components
from fastapi.middleware.cors import CORSMiddleware  # CORS support
from pydantic import BaseModel  # request schema
from groq import Groq  # Groq client
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session  # type hint for a database session
from ingestion.pdf_utils import extract_text_from_pdf
from rag.vector_store import get_documents
from ingestion.ingestion import ingest_document
from rag.chunking import chunk_text
from rag.embeddings import get_embedding
from rag.vector_store import add_chunks
from rag.rag import retrieve_context
from db.database import get_db  # gives us a database session per request
from db.models import Message, RetrievedChunk  # our two database tables
from db.database import engine, Base
import db.models  # noqa: F401 — needed so SQLAlchemy sees the table definitions

# create tables automatically on startup if they don't exist yet
# safe to run every time — SQLAlchemy skips tables that already exist
Base.metadata.create_all(bind=engine)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# DATABASE-BACKED MEMORY (replaces the old in-memory dictionaries)
# ------------------------------------------------------------------
# Before: conversation_histories = {}  <- a Python dictionary, living
# in RAM. Worked fine, but a backend restart wiped everything.
#
# Now: every message is a ROW in the "messages" table in Postgres.
# Instead of dict[session_id] -> list of messages, we now run a
# database QUERY: "give me all messages WHERE session_id = ...".
# Same idea, but it survives a restart because it's saved to disk by
# Postgres, not held in the Python process's memory.
# ------------------------------------------------------------------

# how many of the most recent messages to send back to the LLM as
# context - keeps prompts from growing forever as a chat gets long
MAX_HISTORY_MESSAGES = 6


UPLOAD_DIR = "uploads"  # upload directory

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)  # create uploads folder


client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class ChatRequest(BaseModel):
    message: str
    document: str | None = None
    session_id: str  # <-- NEW: identifies which conversation this belongs to


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"  # save path

    with open(file_path, "wb") as f:
        f.write(await file.read())  # save uploaded file

    chunk_count = ingest_document(
        file_path,
        file.filename
    )  # index document

    print("chunk_count", chunk_count)

    return {
        "message": "File uploaded and indexed successfully",
        "chunks": chunk_count
    }


@app.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):

    # STAGE 1: load this session's recent history from the DATABASE
    # instead of a dictionary. This is a real SQL query under the
    # hood, roughly: "SELECT * FROM messages WHERE session_id = ...
    # ORDER BY id DESC LIMIT 6". db.query(Message) is SQLAlchemy's way
    # of writing that without raw SQL text.
    #
    # We sort NEWEST first + LIMIT, so Postgres only sends us the rows
    # we actually need (not the whole conversation history every time).
    # Then we reverse back to oldest-first, since the LLM should read
    # the conversation in the order it actually happened.
    history_rows = (
        db.query(Message)
        .filter(Message.session_id == request.session_id)
        .order_by(Message.id.desc())
        .limit(MAX_HISTORY_MESSAGES)
        .all()
    )
    history_rows.reverse()

    # retrieve relevant chunks from vector DB (unchanged - this part
    # never touched the dictionaries, it's a separate pipeline)
    context_items = retrieve_context(
        request.message,
        request.document
    )

    # format retrieved chunks for LLM
    context_text = "\n\n".join(
        [
            f"Source: {item['source']}\nContent: {item['content']}"
            for item in context_items
        ]
    )


    # save the user's message as a new ROW in the database (instead
    # of history.append(...) on a Python list)
    user_message_row = Message(
        session_id=request.session_id,
        role="user",
        content=request.message
    )
    db.add(user_message_row)        # stage this row for saving
    db.commit()                      # actually write it to Postgres

    # build prompt messages
    messages = [
        {
            "role": "system",
            "content": (
                "You are a documentation assistant. "
                "Answer only from the provided context. "
                "Mention source documents at the beginning of the answer. "
                "If the answer is not found, say so clearly."
            )
        }
    ]

    # add recent conversation memory FOR THIS SESSION ONLY.
    # history_rows are database ROW objects, not plain dicts, and are
    # already limited to MAX_HISTORY_MESSAGES by the query above - we
    # pull out just .role and .content, since Groq's API only wants
    # those two fields per message.
    messages.extend(
        {"role": m.role, "content": m.content}
        for m in history_rows
    )

    # add current context + question
    messages.append(
        {
            "role": "user",
            "content": f"""
Context:
{context_text}

Question:
{request.message}
"""
        }
    )

    # call LLM
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    assistant_response = response.choices[0].message.content

    sources_list = list(
        {
            item["source"]
            for item in context_items
        }
    )

    # save the assistant's response as a new ROW too, including
    # sources (stored in the JSON column we defined in models.py)
    assistant_message_row = Message(
        session_id=request.session_id,
        role="assistant",
        content=assistant_response,
        sources=sources_list
    )
    db.add(assistant_message_row)
    db.commit()

    # remember the latest retrieved context for THIS session in the
    # database. Simplest approach: delete any old rows for this
    # session first, then insert the new ones - so there's always
    # exactly one "latest" set per session, not a growing pile.
    db.query(RetrievedChunk).filter(
        RetrievedChunk.session_id == request.session_id
    ).delete()

    for item in context_items:
        db.add(RetrievedChunk(
            session_id=request.session_id,
            source=item["source"],
            chunk_index=item["chunk"],
            content=item["content"]
        ))
    db.commit()

    return {
        "response": assistant_response,
        "sources": sources_list,
        # full retrieved chunks - lets the frontend show WHAT text was
        # actually used to answer, not just which filenames it came from
        "retrieved_chunks": context_items
    }


@app.get("/documents")
def documents():
    return {
        "documents": get_documents()
    }


@app.get("/history/{session_id}")
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """
    Lets the frontend ask: 'what messages already exist for this
    session, and what was the last retrieved context?' - called once
    when the page loads, so a refresh can restore both the chat AND
    the context panel instead of showing them blank.

    Now reads from the database instead of in-memory dictionaries -
    this means it survives a backend restart too.
    """
    message_rows = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.id.asc())
        .all()
    )

    # convert database row objects into plain dicts, matching the
    # exact shape the frontend already expects: {role, content, sources?}
    history = [
        {
            "role": m.role,
            "content": m.content,
            "sources": m.sources  # will be None for user messages, a list for assistant ones
        }
        for m in message_rows
    ]

    context_rows = (
        db.query(RetrievedChunk)
        .filter(RetrievedChunk.session_id == session_id)
        .order_by(RetrievedChunk.id.asc())
        .all()
    )

    latest_context = [
        {
            "source": c.source,
            "chunk": c.chunk_index,
            "content": c.content
        }
        for c in context_rows
    ]

    return {
        "history": history,
        "latest_context": latest_context
    }


@app.get("/")
def health_check():
    return {
        "message": "AI Documentation Assistant Running"
    }