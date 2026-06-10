from fastapi import FastAPI, UploadFile, File  # FastAPI components
from fastapi.middleware.cors import CORSMiddleware  # CORS support
from pydantic import BaseModel  # request schema
from groq import Groq  # Groq client
import os
from dotenv import load_dotenv
from ingestion import ingest_document  # document indexing
from rag import retrieve_context  # retrieval pipeline
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"  # upload directory

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)  # create uploads folder


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class ChatRequest(BaseModel):
    message: str


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"  # save path

    with open(file_path, "wb") as f:
        f.write(await file.read())  # save uploaded file

    chunk_count = ingest_document(
        file_path,
        file.filename
    )  # index document

    return {
        "message": "File uploaded and indexed successfully",
        "chunks": chunk_count
    }


@app.post("/chat")
def chat(request: ChatRequest):


    context_items = retrieve_context(
        request.message
    )  # retrieve relevant chunks




    context_text = "\n\n".join(
        [
            f"Source: {item['source']}\nContent: {item['content']}"
            for item in context_items
        ]
    )  # format context
    
    print("retrived context",context_items)
    

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a documentation assistant. "
                    "Answer only from the provided context. "
                    "Mention source documents."
                )
            },
            {
                "role": "user",
                "content": f"""
Context:
{context_text}

Question:
{request.message}
"""
            }
        ]
    )

    return {
        "response": response.choices[0].message.content,
        "sources": list(
            {
                item["source"]
                for item in context_items
            }
        )
    }


@app.get("/")
def health_check():
    return {
        "message": "AI Documentation Assistant Running"
    }
