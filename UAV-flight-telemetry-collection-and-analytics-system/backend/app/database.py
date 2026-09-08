from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = "postgresql://fpv_user:fpv_pass@db:5432/fpv_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    from app.models import flight
    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE flights ADD COLUMN IF NOT EXISTS board_info VARCHAR;"))
        conn.execute(text("ALTER TABLE flights ADD COLUMN IF NOT EXISTS firmware VARCHAR;"))
        conn.execute(text("ALTER TABLE flights ADD COLUMN IF NOT EXISTS track_data TEXT;"))
