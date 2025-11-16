
from pydantic import BaseModel
import os

class Settings(BaseModel):
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "tauon")
    postgres_user: str = os.getenv("POSTGRES_USER", "tauon")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "changeme")

    api_key: str = os.getenv("TAUON_API_KEY", "dev-key")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")

    # LLM/Embeddings
    azure_base: str | None = os.getenv("AZURE_OPENAI_API_BASE")
    azure_key: str | None = os.getenv("AZURE_OPENAI_API_KEY")
    azure_embed: str | None = os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT")
    azure_chat: str | None = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
    azure_version: str | None = os.getenv("AZURE_OPENAI_API_VERSION")

    openai_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_embed_model: str = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")
    openai_chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    st_model: str = os.getenv("SENTENCE_TRANSFORMER", "all-MiniLM-L6-v2")

    # SharePoint
    tenant_id: str | None = os.getenv("MS_TENANT_ID")
    client_id: str | None = os.getenv("MS_CLIENT_ID")
    client_secret: str | None = os.getenv("MS_CLIENT_SECRET")
    sp_site_host: str | None = os.getenv("MS_SP_SITE_HOST")
    sp_site_path: str | None = os.getenv("MS_SP_SITE_PATH")
    sp_drive_name: str | None = os.getenv("MS_SP_DRIVE_NAME")

settings = Settings()
