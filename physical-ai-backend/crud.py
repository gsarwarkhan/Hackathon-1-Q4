import uuid
from typing import List, Optional
from sqlmodel import Session, select
from .database import ChatSession, Message

def get_or_create_session(db: Session, session_id: Optional[str] = None) -> ChatSession:
    if session_id:
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        session_obj = db.exec(statement).first()
        if session_obj:
            return session_obj
    
    # Create new if not found or not provided
    new_id = session_id or str(uuid.uuid4())
    session_obj = ChatSession(session_id=new_id)
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)
    return session_obj

def add_message(db: Session, session_id: str, sender: str, text: str):
    message = Message(session_id=session_id, sender=sender, text=text)
    db.add(message)
    db.commit()

def get_chat_history(db: Session, session_id: str, limit: int = 10) -> List[dict]:
    statement = select(Message).where(Message.session_id == session_id).order_by(Message.created_at.desc()).limit(limit)
    messages = db.exec(statement).all()
    # Reverse to get chronological order
    return [{"role": "user" if m.sender == "user" else "assistant", "content": m.text} for m in reversed(messages)]
