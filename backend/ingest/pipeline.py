
from pathlib import Path
from typing import Optional
from sqlalchemy import text
from db import SessionLocal
from rag.embedder import Embedder
from .extractors import extract_text
from .utils import split_into_chunks

def ingest_path(root: str, source_label: Optional[str] = None):
    root_path = Path(root)
    emb = Embedder()
    with SessionLocal() as s:
        for file in root_path.rglob("*"):
            if not file.is_file():
                continue
            for page_text, page_num in extract_text(file):
                chunks = split_into_chunks(page_text, 1500, 200)
                if not chunks:
                    continue
                vectors = emb.embed(chunks)
                for idx, (chunk, vec) in enumerate(zip(chunks, vectors)):
                    s.execute(text(
                        """
                        INSERT INTO documents (source, uri, page, chunk_id, content, embedding)
                        VALUES (:source, :uri, :page, :chunk_id, :content, :embedding)
                        """
                    ), {
                        "source": source_label or "local",
                        "uri": str(file),
                        "page": page_num,
                        "chunk_id": f"{file.name}#p{page_num}#c{idx}",
                        "content": chunk,
                        "embedding": vec,
                    })
        s.commit()
