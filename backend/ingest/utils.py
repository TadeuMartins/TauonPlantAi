
from typing import List

def split_into_chunks(text: str, max_tokens: int = 800, overlap: int = 100) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    step = max_tokens - overlap
    chunks = []
    for i in range(0, len(text), step):
        chunks.append(text[i:i+max_tokens])
    return chunks
