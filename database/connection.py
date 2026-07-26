"""SQLAlchemy engine/session shared across etl and analytics code."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.config import DATABASE_URL

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)
