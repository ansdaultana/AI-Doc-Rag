"""
database.py — connects our app to a PostgreSQL database.

WHAT IS POSTGRES, IN YOUR TERMS?
-----------------------------------
You already know MySQL - Postgres is the same category of database
(relational: tables, rows, columns, SQL, JOINs, foreign keys). Almost
everything transfers directly. It's running as a real server on your
machine (started with `sudo service postgresql start`).

WHAT IS SQLALCHEMY, SIMPLY?
------------------------------
A library that lets us write plain Python instead of raw SQL text.
It translates our Python into the right SQL for whichever database
we're connected to.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Connection string format for Postgres:
#   postgresql://<username>:<password>@<host>:<port>/<database_name>
#
# Matches the user/database created with:
#   CREATE USER docuser WITH PASSWORD 'docpassword';
#   CREATE DATABASE docassistant OWNER docuser;
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Check your environment configuration."
    )

engine = create_engine(DATABASE_URL)

# SessionLocal is a "factory" for creating database sessions - one
# conversation with the database per request: open it, read/write,
# close it.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base is what our table classes (in models.py) will inherit from.
Base = declarative_base()


def get_db():
    """
    A FastAPI 'dependency' - FastAPI calls this automatically for any
    endpoint that asks for it, handing over a fresh database session
    and cleaning it up afterward (even if an error happens).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()