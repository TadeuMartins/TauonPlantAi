
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import tempfile

from settings import settings
from db import init_db
from ingest.pipeline import ingest_path
from rag.embedder import Embedder
from rag.retriever import Retriever
from rag.chat import ChatLLM

app = FastAPI(title="TauON PlantAI")

origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
embedder = Embedder()
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
