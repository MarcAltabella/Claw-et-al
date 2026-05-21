import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("Database URL not found in .env")

engine = create_engine(SQLALCHEMY_DATABASE_URL) # responsible for sqlalchemy to connect to postgres

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # create a session in SQLAlchemy

Base = declarative_base()

def get_db(): # create a fastapi dependency that creates a database session safely
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()