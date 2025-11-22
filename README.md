
# TauON PlantAI

RAG para documentos industriais com ingestão de **pasta local** (via seleção de diretório no navegador) e **SharePoint** (Microsoft Graph). Backend em FastAPI + Postgres/pgvector e frontend em React.

## Como rodar (dev)

1. Copie `.env.example` para `.env` e preencha as chaves (Postgres, Azure/OpenAI, SharePoint).
2. **Importante sobre embeddings**: O modelo padrão `text-embedding-3-large` usa 3072 dimensões. Se você tiver problemas com dimensionalidade, você pode:
   - Usar `text-embedding-3-small` ou `text-embedding-ada-002` (1536 dimensões) no `.env`
   - Ou, se já tem dados no banco com outra dimensão, execute `docker compose exec postgres psql -U tauon -d tauon -c "DROP TABLE documents;"` e reinicie o backend
3. Suba os serviços:
   ```bash
   docker compose up --build
   ```
4. Acesse:
   - Backend: http://localhost:8000/docs
   - Frontend: http://localhost:5173
5. No Frontend, defina `TAUON_API_KEY` no Local Storage igual ao `TAUON_API_KEY` do `.env`.

> Observação: para `webkitdirectory` (seleção de pasta) use Chrome/Edge.

## Notas
- **Variáveis de ambiente**: O backend carrega explicitamente as variáveis do arquivo `.env` na raiz do projeto usando `python-dotenv` ao rodar localmente (sem Docker). Isso garante que variáveis como `TAUON_API_KEY` e `CORS_ORIGINS` sejam sempre carregadas corretamente. A dependência já está incluída em `backend/requirements.txt`.
- **Embeddings**: O sistema detecta automaticamente a dimensionalidade do modelo:
  - Azure OpenAI ou OpenAI API: `text-embedding-3-large` (3072 dim), `text-embedding-3-small` (1536 dim), `text-embedding-ada-002` (1536 dim)
  - Fallback CPU: sentence-transformers (dimensão detectada automaticamente)
  - A tabela do banco de dados é criada com a dimensão correta na primeira execução
- Suporte de arquivos: PDF, DOCX, TXT, CSV/XLSX (básico) e OCR em imagens.
- **CORS**: O backend está configurado com CORS completo, incluindo tratamento de erros. A variável `CORS_ORIGINS` pode ser configurada no arquivo `.env` (padrão: `http://localhost:5173`). Para múltiplas origens, separe por vírgula. Os headers CORS são incluídos mesmo em respostas de erro (401, 422, 500).
- Melhorias recomendadas: chunking por tokens, reranker, namespaces por projeto e crawling incremental do SharePoint.
