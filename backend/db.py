
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

def init_db(embedding_dimension: int = 3072):
    """
    Initialize database with the correct embedding dimension.
    Default is 3072 for text-embedding-3-large model.
    """
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        
        # Check if table exists and get its dimension
        result = conn.execute(text(
            """
            SELECT column_name, udt_name, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'documents' AND column_name = 'embedding'
            """
        )).fetchone()
        
        if result:
            # Table exists - check if we need to recreate it with new dimension
            # We'll drop and recreate if dimension doesn't match
            # In production, you'd want a proper migration
            print(f"[DB] Table 'documents' already exists. Checking dimension...")
            # Get current dimension from vector type
            dim_result = conn.execute(text(
                """
                SELECT atttypmod - 4 as dimension
                FROM pg_attribute
                WHERE attrelid = 'documents'::regclass AND attname = 'embedding'
                """
            )).fetchone()
            
            if dim_result and dim_result[0] != embedding_dimension:
                print(f"[DB] WARNING: Existing table has dimension {dim_result[0]}, but model requires {embedding_dimension}")
                print(f"[DB] Please run: DROP TABLE documents; to recreate with correct dimension")
                print(f"[DB] Or update your embedding model to match dimension {dim_result[0]}")
        else:
            # Table doesn't exist - create it with the correct dimension
            print(f"[DB] Creating 'documents' table with embedding dimension {embedding_dimension}...")
            conn.execute(text(
                f"""
                CREATE TABLE IF NOT EXISTS documents (
                  id SERIAL PRIMARY KEY,
                  source VARCHAR(512),
                  uri VARCHAR(1024),
                  page INTEGER,
                  chunk_id VARCHAR(128),
                  content TEXT,
                  embedding VECTOR({embedding_dimension})
                );
                """
            ))
            
            # Create IVFFLAT index only if dimension <= 2000 (pgvector limitation)
            # For dimensions > 2000, the table will work but without the IVFFLAT index
            # which may result in slower similarity searches but allows use of large models
            if embedding_dimension <= 2000:
                conn.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops);"
                ))
                print(f"[DB] Created IVFFLAT index for embedding dimension {embedding_dimension}")
            else:
                print(f"[DB] Skipping IVFFLAT index creation: dimension {embedding_dimension} exceeds pgvector limit of 2000")
                print(f"[DB] Similarity searches will work but may be slower without the index")
            
            # Always create source index regardless of embedding dimension
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source);"
            ))
            
            print(f"[DB] Table created successfully with dimension {embedding_dimension}")

