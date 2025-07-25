from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import subprocess, os, requests
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "tavily")

app = FastAPI()

# CORS (allow React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Change if needed
    allow_methods=["*"],
    allow_headers=["*"],
)

def needs_search(prompt):
    keywords = ["latest", "today", "current", "news", "trending"]
    return any(k in prompt.lower() for k in keywords)

def search_web(query):
    if SEARCH_PROVIDER == "tavily":
        r = requests.post(
            "https://api.tavily.com/search",
            headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
            json={"query": query, "search_depth": "basic", "include_answer": True}
        )
        return r.json().get("answer", "")
    elif SEARCH_PROVIDER == "brave":
        r = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY},
            params={"q": query}
        )
        res = r.json().get("web", {}).get("results", [])
        return "\n".join(f"{r['title']}: {r['description']}" for r in res[:3])
    return ""

def query_llama(prompt):
    proc = subprocess.Popen(
        ["ollama", "run", "llama3.1:8b"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    out, _ = proc.communicate(input=prompt.encode())
    return out.decode()

@app.post("/ask")
async def ask(req: Request):
    data = await req.json()
    user_prompt = data.get("prompt", "")

    if not user_prompt.strip():
        return {"response": "Empty prompt."}

    if needs_search(user_prompt):
        context = search_web(user_prompt)
        full_prompt = f"Use this web info:\n{context}\n\nAnswer this:\n{user_prompt}"
    else:
        full_prompt = user_prompt

    answer = query_llama(full_prompt)
    return {"response": answer.strip()}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess, os, requests
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
SEARCH_PROVIDER = os.getenv("SEARCH_PROVIDER", "tavily")

# === FastAPI App ===
app = FastAPI()

# Allow CORS for your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Pydantic Model for Request ===
class AskRequest(BaseModel):
    prompt: str

# === Helper: Should we search the web? ===
def needs_search(prompt: str) -> bool:
    keywords = ["latest", "today", "current", "news", "trending", "who won", "real-time"]
    prompt_lower = prompt.lower()
    result = any(k in prompt_lower for k in keywords) or prompt_lower.startswith("search:")
    print(f"needs_search('{prompt}') = {result}")
    return result

# === Helper: Web search using Tavily or Brave ===
def search_web(query: str) -> str:
    print(f"search_web called with: {query}")
    if SEARCH_PROVIDER == "tavily":
        try:
            r = requests.post(
                "https://api.tavily.com/search",
                headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
                json={"query": query, "search_depth": "basic", "include_answer": True}
            )
            print(f"Tavily response: {r.text}")
            return r.json().get("answer", "")
        except Exception as e:
            print(f"Tavily search error: {e}")
            return f"[Tavily search error: {e}]"
        
    elif SEARCH_PROVIDER == "brave":
        try:
            r = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY},
                params={"q": query}
            )
            res = r.json().get("web", {}).get("results", [])
            return "\n".join(f"{r['title']}: {r['description']}" for r in res[:3])
        except Exception as e:
            return f"[Brave search error: {e}]"

    return ""

# === Helper: Query local LLaMA 3.1 model ===
def query_llama(prompt: str) -> str:
    try:
        proc = subprocess.Popen(
            ["ollama", "run", "llama3.1:8b"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, _ = proc.communicate(input=prompt.encode())
        return out.decode()
    except Exception as e:
        return f"[Ollama error: {e}]"

# === POST /ask endpoint ===
@app.post("/ask")
async def ask(request: AskRequest):
    user_prompt = request.prompt.strip()

    if not user_prompt:
        return {"response": "Empty prompt."}

    if needs_search(user_prompt):
        context = search_web(user_prompt)
        full_prompt = f"Use this web info:\n{context}\n\nThen answer this:\n{user_prompt}"
    else:
        full_prompt = user_prompt

    answer = query_llama(full_prompt)
    return {"response": answer.strip()}
