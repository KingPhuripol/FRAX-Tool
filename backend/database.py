from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── รองรับ Docker Volume: ถ้ามี ENV DATABASE_PATH ให้ใช้ path นั้น ──
_env_db = os.environ.get("DATABASE_PATH")
if _env_db:
    DATABASE_URL = f"sqlite:///{_env_db}"
else:
    DATABASE_URL = f"sqlite:///{BASE_DIR}/frax_patients.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
