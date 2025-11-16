
from typing import List
import numpy as np
from settings import settings

class Embedder:
    def __init__(self):
        self.mode = None
        if settings.azure_base and settings.azure_key:
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                api_key=settings.azure_key,
                api_version=settings.azure_version,
                azure_endpoint=settings.azure_base,
            )
            self.deployment = settings.azure_embed
            self.mode = "azure"
        elif settings.openai_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.openai_key)
            self.model = settings.openai_embed_model
            self.mode = "openai"
        else:
            from sentence_transformers import SentenceTransformer
            self.st = SentenceTransformer(settings.st_model)
            self.mode = "st"

    def embed(self, texts: List[str]) -> List[List[float]]:
        if self.mode == "azure":
            res = self.client.embeddings.create(input=texts, model=self.deployment)
            return [d.embedding for d in res.data]
        if self.mode == "openai":
            res = self.client.embeddings.create(input=texts, model=self.model)
            return [d.embedding for d in res.data]
        embs = self.st.encode(texts, normalize_embeddings=True)
        return [e.tolist() for e in embs]
