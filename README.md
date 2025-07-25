# Local LLM Agent MVP

A minimal full-stack chat interface using a local Llama 3.1 model.

## Features

- React + Vite frontend for chatting with the LLM
- FastAPI backend with optional web search (Tavily/Brave)
- No database (stateless), but ready for DB integration

## Getting Started
### Backend

```sh
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```sh
cd frontend
npm install
npm run dev
```