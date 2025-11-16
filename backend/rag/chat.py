
from typing import List, Dict
from settings import settings

class ChatLLM:
    def __init__(self):
        self.mode = None
        if settings.azure_base and settings.azure_key:
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                api_key=settings.azure_key,
                api_version=settings.azure_version,
                azure_endpoint=settings.azure_base,
            )
            self.model = settings.azure_chat
            self.mode = "azure"
        else:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.openai_key)
            self.model = settings.openai_chat_model
            self.mode = "openai"

    def answer(self, question: str, contexts: List[Dict]):
        sys = (
            "You are TauON PlantAI, an industrial RAG assistant. Answer using only the provided context."
            " If unsure, say you don't know. Always cite sources as [filename p.X] inline."
        )
        ctx_blocks = []
        for i, c in enumerate(contexts, start=1):
            src = c.get("source") or c.get("uri")
            page = c.get("page") or 1
            ctx_blocks.append(f"[DOC{i}] {src} (p.{page})\\n{c['content'][:2000]}")
        prompt = "\\n\\n".join(ctx_blocks) + f"\\n\\nQuestion: {question}"
        msgs = [
            {"role": "system", "content": sys},
            {"role": "user", "content": prompt},
        ]
        if self.mode == "azure":
            resp = self.client.chat.completions.create(model=self.model, messages=msgs)
            return resp.choices[0].message.content
        else:
            resp = self.client.chat.completions.create(model=self.model, messages=msgs)
            return resp.choices[0].message.content
