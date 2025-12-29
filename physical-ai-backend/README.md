# Physical AI & Humanoid Robotics - Canonical Backend

This is the production-ready backend for the Physical AI & Humanoid Robotics platform. It uses FastAPI for the API, Qdrant for vector search (RAG), and SQLModel for chat persistence.

## 🛠️ Features
- **RAG Integration**: Search textbook context using Qdrant + FastEmbed.
- **Chat Persistence**: Stores sessions and messages in SQLite/PostgreSQL.
- **Rate Limiting**: Protected against abuse (10 requests/min).
- **Environment Driven**: No hardcoded secrets.

## 🚀 Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment**:
    Copy `.env.example` to `.env` and fill in your credentials from Qdrant Cloud and OpenRouter.

3.  **Index Textbook Content**:
    ```bash
    python utils/reindex.py
    ```

4.  **Run Locally**:
    ```bash
    uvicorn main:app --reload
    ```

## 🚢 Deployment

### Recommended: Render (Free)
1.  Connect this repository to Render.
2.  Choose "Web Service".
3.  Runtime: **Python**.
4.  Build Command: `pip install -r requirements.txt`.
5.  Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
6.  Add all variables from `.env` to Render Environment settings.

### Recommended: Railway (No-card free tier)
1.  Connect repository.
2.  Standard Python deployment will work.
3.  Add env vars.

## 🔗 Frontend Connection
Ensure `ALLOWED_ORIGINS` in your backend `.env` matches your Vercel URL.
Update `REACT_APP_BACKEND_URL` in your Vercel frontend to point to this backend's live URL.
