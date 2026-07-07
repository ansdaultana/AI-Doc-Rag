# 📚 AI Documentation Assistant (RAG)

> A Retrieval-Augmented Generation (RAG) application that enables users to upload PDF documents and ask natural language questions. The assistant retrieves relevant document context using semantic search and generates accurate responses with Groq LLM.

🌐 **Live Demo:** https://docassistant-frontend.onrender.com/

---

## 🚀 Features

- Upload and process PDF documents
- Semantic search using vector embeddings
- AI-powered question answering with Groq
- Conversation history stored in PostgreSQL
- FastAPI REST API
- React + Vite frontend
- Docker support for containerized deployment
- Fully deployed on Render

---

## 🏗️ Architecture

```text
                PDF Upload
                     │
                     ▼
              Text Extraction
                     │
                     ▼
             Chunking Documents
                     │
                     ▼
          Generate Embeddings
                     │
                     ▼
                ChromaDB
                     │
                     ▼
              Similarity Search
                     │
                     ▼
      Retrieved Context + User Query
                     │
                     ▼
                  Groq LLM
                     │
                     ▼
                AI Response
```

---

## ⚙️ Tech Stack

| Category | Technologies |
|----------|--------------|
| Backend | FastAPI, Python |
| Frontend | React, Vite |
| Vector Database | ChromaDB |
| LLM | Groq API |
| Embeddings | FastEmbed |
| Database | PostgreSQL |
| PDF Processing | PyPDF |
| Chunking | LangChain Text Splitters |
| ORM | SQLAlchemy |
| Containerization | Docker, Docker Compose |
| Deployment | Render |

---

## 📂 Project Structure

```
AI-Doc-Rag/
│
├── backend/
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── database/
│   └── main.py
│
├── frontend/
│
├── docker-compose.yml
└── README.md
```

---

## 🔄 Workflow

1. Upload a PDF document.
2. Extract text from the document.
3. Split text into smaller chunks.
4. Generate vector embeddings using FastEmbed.
5. Store embeddings in ChromaDB.
6. User submits a question.
7. Retrieve the most relevant document chunks.
8. Send the retrieved context and user query to Groq LLM.
9. Return an AI-generated response.

---

## 📦 Libraries Used

| Library | Purpose |
|----------|---------|
| FastAPI | REST API framework |
| ChromaDB | Vector database |
| FastEmbed | Embedding generation |
| Groq | Large Language Model inference |
| PyPDF | PDF text extraction |
| SQLAlchemy | Database ORM |
| psycopg2 | PostgreSQL driver |
| LangChain Text Splitters | Document chunking |
| tiktoken | Token counting |
| python-dotenv | Environment variable management |

---

## 🚀 Running Locally

```bash
git clone https://github.com/ansdaultana/AI-Doc-Rag.git

cd AI-Doc-Rag

docker-compose up --build
```

Or run the frontend and backend separately.

---

## 🌐 Deployment

The application is deployed on **Render**.

**Live Demo**

https://docassistant-frontend.onrender.com/

---

## 🔮 Future Improvements

- Support multiple document uploads
- Hybrid keyword + semantic search
- Authentication and user accounts
- Streaming LLM responses
- OCR support for scanned PDFs
- Document management dashboard

---

## 👨‍💻 Author

**Ans Nazir**

Computer Science Graduate | Software Engineer

GitHub: https://github.com/ansdaultana