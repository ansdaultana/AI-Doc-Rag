from fastapi import FastAPI, UploadFile, File  # FastAPI components
from fastapi.middleware.cors import CORSMiddleware  # CORS support
from pydantic import BaseModel  # request schema
from groq import Groq  # Groq client
import os
from dotenv import load_dotenv
from ingestion import ingest_document  # document indexing
from rag import retrieve_context  # retrieval pipeline
from vector_store import get_documents


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
# SESSION-BASED MEMORY
# ------------------------------------------------------------------
# Before: conversation_history = []  <- ONE list shared by EVERY user.
# That's like everyone in a building sharing a single notebook -
# whatever you write, the next person's words land right after yours.
#
# Now: a DICTIONARY where each session gets its own list.
#   {
#     "session-abc-123": [ {role: user, content: ...}, ... ],
#     "session-xyz-789": [ {role: user, content: ...}, ... ],
#   }
# The frontend generates a random session_id once per browser tab and
# sends it with every /chat request. We use that id as the "drawer
# label" to find (or create) that session's own conversation list.
# ------------------------------------------------------------------
conversation_histories: dict[str, list[dict]] = {}

# how many of the most recent messages to send back to the LLM as
# context - keeps prompts from growing forever as a chat gets long
MAX_HISTORY_MESSAGES = 6


def get_history(session_id: str) -> list[dict]:
    """
    Returns the conversation list for this session_id, creating an
    empty one first if this session hasn't been seen before.
    This is the 'open the right drawer, or make a new one' step.
    """
    if session_id not in conversation_histories:
        conversation_histories[session_id] = []
    return conversation_histories[session_id]


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
def chat(request: ChatRequest):

    # get THIS session's own conversation list (not the global one)
    history = get_history(request.session_id)

    # retrieve relevant chunks from vector DB
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

    print("retrieved context:", context_items)

    # save user message into THIS session's history
    history.append(
        {
            "role": "user",
            "content": request.message
        }
    )

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

    # add recent conversation memory FOR THIS SESSION ONLY
    messages.extend(
        history[-MAX_HISTORY_MESSAGES:]
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

    # save assistant response into THIS session's history
    history.append(
        {
            "role": "assistant",
            "content": assistant_response
        }
    )

    return {
        "response": assistant_response,
        "sources": list(
            {
                item["source"]
                for item in context_items
            }
        ),
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
def get_chat_history(session_id: str):
    """
    Lets the frontend ask: 'what messages already exist for this
    session?' - called once when the page loads, so a refresh can
    redisplay past messages instead of showing a blank chat.
    """
    return {
        "history": get_history(session_id)
    }


@app.get("/")
def health_check():
    return {
        "message": "AI Documentation Assistant Running"
    }