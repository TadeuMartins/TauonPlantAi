
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path
import shutil
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
# This ensures correct loading of variables like TAUON_API_KEY and CORS_ORIGINS
# when running locally without Docker
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

from settings import settings
from db import init_db
from ingest.pipeline import ingest_path
from rag.embedder import Embedder
from rag.retriever import Retriever
from rag.chat import ChatLLM

app = FastAPI(title="TauON PlantAI")

# Configure CORS to allow frontend requests
# CORS_ORIGINS can be set in .env file (e.g., "http://localhost:5173,http://localhost:3000")
origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers to ensure CORS headers are included in error responses
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"Access-Control-Allow-Origin": request.headers.get("origin", "*")}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
        headers={"Access-Control-Allow-Origin": request.headers.get("origin", "*")}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
        headers={"Access-Control-Allow-Origin": request.headers.get("origin", "*")}
    )

# Initialize embedder first to detect dimension
embedder = Embedder()

# Initialize database with the correct embedding dimension
init_db(embedding_dimension=embedder.dimension)

retriever = Retriever(k=8)
llm = ChatLLM()

def check_auth(x_api_key: str):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.post("/ingest/local")
async def ingest_local(x_api_key: str = Form(...), path: str = Form(...)):
    check_auth(x_api_key)
    ingest_path(path, source_label="local")
    return {"status": "ok"}

@app.post("/ingest/folder-upload")
async def ingest_folder_upload(x_api_key: str = Form(...), files: list[UploadFile] = File(...)):
    check_auth(x_api_key)
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        for f in files:
            p = base / f.filename
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("wb") as out:
                shutil.copyfileobj(f.file, out)
        ingest_path(tmp, source_label="upload")
    return {"status": "ok"}

@app.post("/ingest/sharepoint")
async def ingest_sharepoint(x_api_key: str = Form(...), sp_folder: str = Form(...)):
    check_auth(x_api_key)
    from ingest.sharepoint_client import SharePointClient
    sp = SharePointClient()
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        async def run():
            async for name, content in sp.iter_files(sp_folder):
                p = base / name
                p.parent.mkdir(parents=True, exist_ok=True)
                with p.open("wb") as out:
                    out.write(content)
        await run()
        ingest_path(tmp, source_label="sharepoint")
    return {"status": "ok"}

@app.post("/chat")
async def chat(x_api_key: str = Form(...), question: str = Form(...)):
    check_auth(x_api_key)
    q_emb = embedder.embed([question])[0]
    hits = retriever.search(q_emb)
    answer = llm.answer(question, hits)
    return JSONResponse({"answer": answer, "sources": hits})
