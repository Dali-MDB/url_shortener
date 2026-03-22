from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker,Session
from typing import Annotated
from fastapi import Depends
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
engine = create_engine(url=SUPABASE_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db =  SessionLocal()
    try:        
        yield db
    finally:
        db.close()
    
SessionDep = Annotated[Session,Depends(get_db)]
    

class Base(DeclarativeBase):
    pass