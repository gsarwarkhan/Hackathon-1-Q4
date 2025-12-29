import os
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select

# Models
class ChatSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List["Message"] = Relationship(back_populates="session")

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="chatsession.session_id")
    sender: str  # 'user' or 'ai'
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    session: ChatSession = Relationship(back_populates="messages")

# Engine setup
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./database.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
