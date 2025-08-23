# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_DIR = os.getenv("DB_DIR", "/app/data")
DB_FILE = os.getenv("DB_FILE", "reavaliacao.db")
os.makedirs(DB_DIR, exist_ok=True)

DB_URL = f"sqlite:///{os.path.join(DB_DIR, DB_FILE)}"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
