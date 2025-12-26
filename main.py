from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse # Import JSONResponse
from pydantic import BaseModel, Field # Import Field for APIErrorResponse
from typing import List, Dict, Optional
from uuid import UUID, uuid4
from sqlmodel import Session, select
from datetime import datetime
import logging # Import logging

from router import ai_wrapper
from database import ChatSession, Message, create_db_and_tables, engine 
from crud import ( # Import CRUD functions
    get_chat_session_by_id, 
    create_new_chat_session, 
    get_messages_for_session, 
    add_message_to_session
)

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: Optional[UUID] = None
    message: str

# Define API response models for structured output
class APIResponse(BaseModel):
    status: str = "success"
    message: Optional[str] = None
    data: Optional[Dict] = None

class APIErrorResponse(BaseModel):
    status: str = "error"
    message: str = Field(..., description="A detailed error message.")
    code: Optional[int] = Field(None, description="An optional error code.")

def get_session():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Physical AI & Humanoid Robotics Chatbot is healthy"}

@app.post("/chat", response_model=APIResponse, responses={
    400: {"model": APIErrorResponse, "description": "Invalid Request"},
    500: {"model": APIErrorResponse, "description": "Internal Server Error"},
    502: {"model": APIErrorResponse, "description": "AI Service Error"}
})
async def chat(request: ChatRequest, db_session: Session = Depends(get_session)):
    try:
        chat_session: Optional[ChatSession] = None

        if request.session_id:
            chat_session = get_chat_session_by_id(db_session, request.session_id)

        if not chat_session:
            chat_session = create_new_chat_session(db_session)
            logger.info(f"Created new session: {chat_session.id}")

        # Retrieve messages for the current session from DB
        db_messages = get_messages_for_session(db_session, chat_session.id)
        
        # Convert DB messages to AIWrapper format
        current_conversation_history = [
            {"sender": msg.sender, "text": msg.text} for msg in db_messages
        ]

        # Add the new user message to the conversation history (for AI processing)
        new_user_message_dict = {"sender": "user", "text": request.message}
        current_conversation_history.append(new_user_message_dict)

        # Save user message to DB
        add_message_to_session(db_session, chat_session.id, "user", request.message)

        # Get AI response
        ai_response_text = ai_wrapper.get_ai_response(current_conversation_history)

        # Save AI message to DB
        add_message_to_session(db_session, chat_session.id, "ai", ai_response_text)

        return APIResponse(
            status="success", 
            data={"response": ai_response_text, "session_id": chat_session.id}
        )

    except ValueError as e: # Catch specific AI errors from router.py
        logger.error(f"AI Service Error for session {request.session_id}: {e}")
        return JSONResponse(
            status_code=502,
            content=APIErrorResponse(status="error", message=str(e), code=502).dict()
        )
    except HTTPException as e:
        logger.warning(f"HTTP Exception caught: {e.detail}")
        raise e # Re-raise FastAPI HTTPExceptions
    except Exception as e:
        logger.exception(f"An unexpected internal server error occurred for session {request.session_id}.") # Log full traceback
        return JSONResponse(
            status_code=500,
            content=APIErrorResponse(status="error", message="An unexpected internal server error occurred.", code=500).dict()
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
