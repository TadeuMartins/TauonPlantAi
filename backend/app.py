
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path
import shutil
import tempfile
import os
import logging
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
# This ensures correct loading of variables like TAUON_API_KEY and CORS_ORIGINS
# when running locally without Docker
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    """
    Check API key authentication.
    
    This function validates the provided API key against the configured key in settings.
    It logs authentication attempts for diagnostics.
    
    Args:
        x_api_key: The API key provided by the client
        
    Raises:
        HTTPException: 401 Unauthorized if the API key is invalid
    """
    # Mask API keys for logging security (show only first 4 and last 4 characters)
    def mask_key(key: str) -> str:
        if len(key) <= 8:
            return "***"
        return f"{key[:4]}...{key[-4:]}"
    
    received_key_masked = mask_key(x_api_key) if x_api_key else "None"
    expected_key_masked = mask_key(settings.api_key)
    
    logger.info(f"Authentication attempt - Received key: {received_key_masked}, Expected key: {expected_key_masked}")
    
    if x_api_key != settings.api_key:
        logger.error(f"Authentication failed - Invalid API key. Received: {received_key_masked}, Expected: {expected_key_masked}")
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    logger.info("Authentication successful")


@app.post("/ingest/local")
async def ingest_local(x_api_key: str = Form(...), path: str = Form(...)):
    check_auth(x_api_key)
    ingest_path(path, source_label="local")
    return {"status": "ok"}

@app.post("/ingest/folder-upload")
async def ingest_folder_upload(x_api_key: str = Form(...), files: list[UploadFile] = File(...)):
    """
    Ingest files from a folder upload.
    
    This endpoint receives multiple files, saves them to a temporary directory,
    and processes them through the ingestion pipeline.
    
    Authentication is required via x_api_key form parameter.
    """
    logger.info(f"Starting /ingest/folder-upload - Received {len(files)} files")
    
    try:
        # Check authentication with detailed logging
        check_auth(x_api_key)
        
        logger.info(f"Processing {len(files)} uploaded files")
        
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            logger.info(f"Created temporary directory: {tmp}")
            
            for i, f in enumerate(files, 1):
                logger.info(f"Processing file {i}/{len(files)}: {f.filename}")
                p = base / f.filename
                p.parent.mkdir(parents=True, exist_ok=True)
                with p.open("wb") as out:
                    shutil.copyfileobj(f.file, out)
                logger.info(f"Saved file: {p}")
            
            logger.info(f"Starting ingestion pipeline for {tmp}")
            ingest_path(tmp, source_label="upload")
            logger.info("Ingestion pipeline completed successfully")
        
        return {"status": "ok"}
    
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions (like 401 from check_auth) without modification
        logger.error(f"HTTP exception in /ingest/folder-upload: {http_exc.status_code} - {http_exc.detail}")
        raise
    
    except Exception as e:
        # Log the full traceback for debugging
        logger.error("Exception occurred in /ingest/folder-upload endpoint:")
        logger.error(traceback.format_exc())
        
        # Return detailed error response with CORS headers
        error_detail = {
            "error": "Internal server error",
            "message": str(e),
            "type": type(e).__name__
        }
        logger.error(f"Returning error response: {error_detail}")
        
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )


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
