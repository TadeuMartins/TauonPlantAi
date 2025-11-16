
# TauON PlantAI

RAG para documentos industriais com ingestão de **pasta local** (via seleção de diretório no navegador) e **SharePoint** (Microsoft Graph). Backend em FastAPI + Postgres/pgvector e frontend em React.

## Como rodar (dev)

1. Copie `.env.example` para `.env` e preencha as chaves (Postgres, Azure/OpenAI, SharePoint).
2. Suba os serviços:
   ```bash
   docker compose up --build
   ```
3. Acesse:
   - Backend: http://localhost:8000/docs
   - Frontend: http://localhost:5173
4. No Frontend, defina `TAUON_API_KEY` no Local Storage igual ao `TAUON_API_KEY` do `.env`.

> Observação: para `webkitdirectory` (seleção de pasta) use Chrome/Edge.

## Notas
- Embeddings: Azure OpenAI ou OpenAI; fallback CPU (sentence-transformers).
- Suporte de arquivos: PDF, DOCX, TXT, CSV/XLSX (básico) e OCR em imagens.
- **CORS**: O backend já está configurado com CORS. Se tiver problemas de CORS, verifique a variável `CORS_ORIGINS` no arquivo `.env` (padrão: `http://localhost:5173`). Para múltiplas origens, separe por vírgula.
- Melhorias recomendadas: chunking por tokens, reranker, namespaces por projeto e crawling incremental do SharePoint.
