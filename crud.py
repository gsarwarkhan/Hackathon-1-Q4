# crud.py
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select

from database import ChatSession, Message

def get_chat_session_by_id(db_session: Session, session_id: UUID) -> Optional[ChatSession]:
    """Retrieve a chat session by its UUID."""
    return db_session.exec(
        select(ChatSession).where(ChatSession.id == session_id)
    ).first()

def create_new_chat_session(db_session: Session) -> ChatSession:
    """Create and persist a new chat session."""
    session = ChatSession()
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session

def get_messages_for_session(db_session: Session, session_id: UUID) -> List[Message]:
    """Retrieve all messages for a given session, ordered by timestamp."""
    return db_session.exec(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.timestamp)
    ).all()

def add_message_to_session(db_session: Session, session_id: UUID, sender: str, text: str) -> Message:
    """Add a new message to a specific chat session."""
    message = Message(session_id=session_id, sender=sender, text=text)
    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)
    return message
