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

conversation_history = []  # stores chat messages

UPLOAD_DIR = "uploads"  # upload directory

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)  # create uploads folder


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    document: str | None = None


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"  # save path

    with open(file_path, "wb") as f:
        f.write(await file.read())  # save uploaded file

    chunk_count = ingest_document(
        file_path,
        file.filename
    )  # index document


    print("chunk_count",chunk_count)
    
    return {
        "message": "File uploaded and indexed successfully",
        "chunks": chunk_count
    }


@app.post("/chat")
def chat(request: ChatRequest):

    # retrieve relevant chunks from vector DB
    context_items = retrieve_context(
    request.message,
    request.document
    )

    # no relevant chunks found


    # format retrieved chunks for LLM
    context_text = "\n\n".join(
        [
            f"Source: {item['source']}\nContent: {item['content']}"
            for item in context_items
        ]
    )

    print("retrieved context:", context_items)

    # save user message in memory
    conversation_history.append(
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

    # add recent conversation memory
    messages.extend(
        conversation_history[-6:]
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

    # save assistant response in memory
    conversation_history.append(
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
        )
    }


@app.get("/documents")
def documents():
    return {
        "documents": get_documents()
    }
        
@app.get("/")
def health_check():
    return {
        "message": "AI Documentation Assistant Running"
    }

