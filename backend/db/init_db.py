"""
init_db.py — run this ONCE to create the database tables.

HOW TO RUN THIS:
    python init_db.py

WHAT HAPPENS:
    Connects to your Postgres database (docassistant) and creates the
    "messages" and "retrieved_chunks" tables defined in models.py.
"""

from db.database import engine, Base
import db.models  # noqa: F401  (import needed so SQLAlchemy "sees" the tables)

print("Connecting to Postgres and creating tables...")
Base.metadata.create_all(bind=engine)
print("Done. Tables 'messages' and 'retrieved_chunks' now exist in 'docassistant'.")