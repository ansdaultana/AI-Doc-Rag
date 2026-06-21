"""
models.py — defines our database TABLES as Python classes.

NO AUTH, NO USER TABLE
-------------------------
Everything is keyed by session_id directly - the same random ID
already generated in the frontend and saved in localStorage. This
replaces the two Python dictionaries we had before
(conversation_histories and latest_context_by_session) with real
database tables that survive a backend restart.

TWO TABLES:
    Message         - one row per chat message
    RetrievedChunk  - one row per retrieved chunk from the latest question
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from db.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    # which conversation this message belongs to - same role as the
    # dictionary key in the old conversation_histories[session_id]
    session_id = Column(String, index=True, nullable=False)

    role = Column(String, nullable=False)       # "user" or "assistant"
    content = Column(Text, nullable=False)        # the message text

    # stores a list of source filenames, e.g. ["manual.pdf", "guide.pdf"]
    # only assistant messages have this
    sources = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RetrievedChunk(Base):
    __tablename__ = "retrieved_chunks"

    id = Column(Integer, primary_key=True, index=True)

    # which session this retrieval belongs to
    session_id = Column(String, index=True, nullable=False)

    source = Column(String, nullable=False)        # filename, e.g. "manual.pdf"
    chunk_index = Column(Integer, nullable=False)    # position in original doc
    content = Column(Text, nullable=False)           # the actual chunk text

    created_at = Column(DateTime(timezone=True), server_default=func.now())