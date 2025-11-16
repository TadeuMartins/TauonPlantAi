
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from settings import settings

DSN = (
    f"postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
)
engine = create_engine(DSN)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS documents (
              id SERIAL PRIMARY KEY,
              source VARCHAR(512),
              uri VARCHAR(1024),
              page INTEGER,
              chunk_id VARCHAR(128),
              content TEXT,
              embedding VECTOR(1536)
            );
            CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops);
            CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source);
            """
        ))
