
from sqlalchemy import text
from db import SessionLocal
from typing import List, Dict

class Retriever:
    def __init__(self, k: int = 8):
        self.k = k

    def search(self, query_emb: list[float]) -> List[Dict]:
        with SessionLocal() as s:
            sql = text(
                """
                SELECT id, source, uri, page, chunk_id, content,
                       1 - (embedding <=> :q)::float AS score
                FROM documents
                ORDER BY embedding <-> :q
                LIMIT :k
                """
            )
            rows = s.execute(sql, {"q": query_emb, "k": self.k}).mappings().all()
            return [dict(r) for r in rows]
