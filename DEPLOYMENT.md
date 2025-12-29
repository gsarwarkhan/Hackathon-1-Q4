# Deployment Guide - Physical AI & Humanoid Robotics

This project is split into two parts:
1.  **Frontend**: A Docusaurus-based static site (This repository).
2.  **Backend**: A FastAPI-based RAG system ([physical-ai-backend](https://github.com/gsarwarkhan/physical-ai-backend)).

## 🎯 Frontend Deployment (Vercel)

1.  Connect this repository to Vercel.
2.  Framework Preset: **Docusaurus**.
3.  Add environment variable `REACT_APP_BACKEND_URL` pointing to your deployed backend.
4.  Deploy.

## 🚀 Backend Deployment (Railway/Render)

1.  Deploy the `physical-ai-backend` repository.
2.  Configure environment variables in the backend:
    *   `QDRANT_URL`, `QDRANT_API_KEY`
    *   `OPENROUTER_API_KEY`
    *   `DATABASE_URL` (SQLite or PostgreSQL)
3.  Ensure CORS is configured correctly to allow your frontend domain.

## ✅ Verification Checklist

- [ ] "Biography" page loads correctly.
- [ ] "Ask the AI" page loads and connects to the backend.
- [ ] Textbook content is readable without any AI overlap.
- [ ] Dark mode and Urdu localization work as expected.
