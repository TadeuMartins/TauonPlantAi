
from typing import List
import numpy as np
from settings import settings

class Embedder:
    def __init__(self):
        self.mode = None
        self.dimension = 1536  # Default dimension
        
        if settings.azure_base and settings.azure_key:
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                api_key=settings.azure_key,
                api_version=settings.azure_version,
                azure_endpoint=settings.azure_base,
            )
            self.deployment = settings.azure_embed
            self.mode = "azure"
            # Azure embeddings are typically 1536 dimensions
            self.dimension = 1536
        elif settings.openai_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.openai_key)
            self.model = settings.openai_embed_model
            self.mode = "openai"
            # Detect dimension based on model
            if "text-embedding-3-large" in self.model:
                self.dimension = 3072
            elif "text-embedding-3-small" in self.model:
                self.dimension = 1536
            elif "text-embedding-ada-002" in self.model:
                self.dimension = 1536
            else:
                # Default for unknown models
                self.dimension = 1536
        else:
            from sentence_transformers import SentenceTransformer
            self.st = SentenceTransformer(settings.st_model)
            self.mode = "st"
            # Get dimension from the model
            self.dimension = self.st.get_sentence_embedding_dimension()

    def embed(self, texts: List[str]) -> List[List[float]]:
        if self.mode == "azure":
            res = self.client.embeddings.create(input=texts, model=self.deployment)
            return [d.embedding for d in res.data]
        if self.mode == "openai":
            res = self.client.embeddings.create(input=texts, model=self.model)
            return [d.embedding for d in res.data]
        embs = self.st.encode(texts, normalize_embeddings=True)
        return [e.tolist() for e in embs]
