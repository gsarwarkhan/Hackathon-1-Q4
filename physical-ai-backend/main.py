import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from pydantic import BaseModel
from typing import Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from openai import OpenAI
from dotenv import load_dotenv

from .database import get_session, create_db_and_tables
from .crud import get_or_create_session, add_message, get_chat_history
from .rag import get_relevant_context

load_dotenv()

# App Initialization
app = FastAPI(title="Physical AI & Humanoid Robotics Backend")

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
origins = os.getenv("ALLOWED_ORIGINS", "https://hackathon-1-q4.vercel.app").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI Client
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
)
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    status: str = "success"

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def health_check():
    return {"status": "online", "message": "Physical AI Backend is running"}

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, chat_req: ChatRequest, db: Session = Depends(get_session)):
    try:
        # 1. Manage Session
        session_obj = get_or_create_session(db, chat_req.session_id)
        current_session_id = session_obj.session_id
        
        # 2. Add user message to DB
        add_message(db, current_session_id, "user", chat_req.message)
        
        # 3. Get history (last 5 rounds)
        history = get_chat_history(db, current_session_id, limit=10)
        
        # 4. Perform RAG
        context = get_relevant_context(chat_req.message)
        
        # 5. Build System Prompt
        system_prompt = f"""You are an expert AI Assistant specializing in Physical AI and Humanoid Robotics. 
        Answer questions based ONLY on the provided textbook context. If the answer is not in the context, 
        state that you don't know but mention it might be covered in later chapters.
        
        CONTEXT FROM TEXTBOOK:
        {context}
        """
        
        messages = [{"role": "system", "content": system_prompt}] + history
        
        # 6. Call LLM
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.3
        )
        
        ai_text = response.choices[0].message.content
        
        # 7. Add AI response to DB
        add_message(db, current_session_id, "ai", ai_text)
        
        return ChatResponse(response=ai_text, session_id=current_session_id)
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
