# RAG CLI with Postgres + Vertex AI

This repository provides a small Retrieval-Augmented Generation (RAG) CLI example that:

- Uses PostgreSQL as the source of truth (documents stored in a table).
- Uses Google Vertex AI for embeddings and generation (API key authentication).
- Provides an offline-safe local embedding cache and a file-based ingestion queue.
- Exposes a CLI to ingest documents, process the ingestion queue, and run an interactive chat.

Files of interest:
- `rag/cli.py` - CLI entrypoint
- `rag/db.py` - Postgres helper (create tables, insert, fetch)
- `rag/vertex.py` - Vertex AI wrapper for embeddings & generation
- `rag/cache.py` - local embedding cache
- `rag/ingest.py` - queueing and queue worker
- `data/test_docs.json` - small test dataset

Setup (Windows PowerShell):

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Set environment variables (store credentials securely). For local testing you can set them in the shell:

```powershell
$env:DATABASE_URL = 'postgresql://postgres:Anuj%402028@localhost:5432/arogya_swarm'
$env:VERTEX_API_KEY = 'AIzaSyCuB3IMpCRLWioBF5l1ee6R6gpfiIPCS8w'
# You must provide your Vertex project id too
$env:VERTEX_PROJECT_ID = '<YOUR_VERTEX_PROJECT_ID>'
```

3. Initialize DB tables (the CLI does this automatically when processing ingestion).

4. Ingest the provided test docs into the queue and process them:

```powershell
python -m rag.cli ingest --file data/test_docs.json
python -m rag.cli process-queue
```

5. Start the interactive chat:

```powershell
python -m rag.cli chat
```

Notes and caveats:
- This example uses simple in-Python cosine similarity over embeddings fetched from Postgres. It's fine for small datasets and demonstration, but not optimized for large-scale production. For production, enable `pgvector` or an external vector DB.
- Vertex API usage: this code calls Vertex HTTP endpoints using the provided `VERTEX_API_KEY` and requires `VERTEX_PROJECT_ID`. If you use a different model or location, adjust `rag/vertex.py` accordingly.
- Embeddings and generation API shapes may vary; if you receive errors, verify the model names and Vertex region.
# RAG Chatbot (Postgres -> Chroma) — CLI

This project provides a simple Retrieval-Augmented Generation (RAG) CLI chatbot that:

- Reads text data from a Postgres database using a SQL query
- Creates embeddings (OpenAI) and stores them in a local Chroma vector store
- Runs a retrieval-augmented chat loop using OpenAI LLM

**Important environment variables**
- `PROVIDER` (optional) — `openai` (default) or `google` to use Google Gemini / Vertex AI
- `OPENAI_API_KEY` — required if using OpenAI provider (set to your OpenAI API key)
- `OPENAI_MODEL` (optional) — model name for the LLM (default: `gpt-3.5-turbo`)

Note: This is a simple starter. For production, tighten security, add batching, error handling, and a persistent vector DB tuned to your needs.

Setup (Windows PowerShell)

1. Create and activate a virtual environment (optional but recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Set your OpenAI API key (replace with your key):

```powershell
$env:OPENAI_API_KEY = 'sk-...'
```

Optional: set `OPENAI_MODEL` env var (e.g., `gpt-3.5-turbo`).

Using Google Gemini (Vertex AI)

This project can use Google Gemini (Vertex AI) instead of OpenAI. Steps:

1. Install optional Google packages:

```powershell
pip install google-cloud-aiplatform google-auth
```

2. Create a Google Cloud service account with Vertex AI permissions and download the JSON key.
3. Set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` pointing to the JSON key file:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = 'C:\path\to\service-account.json'
$env:PROVIDER = 'google'
```

4. Ingest and chat exactly as with OpenAI; the CLI will use the `PROVIDER` env var or the `--provider` flag.

Note: LangChain's VertexAI integration requires recent LangChain and `google-cloud-aiplatform`. If you see errors, install the packages and follow Google VertexAI auth docs.

Using a Google API key directly

If you already have a Google API key (for example, `AIza...`) and Vertex AI is enabled on your project, you can export it in PowerShell for this session. This is less common than using a service-account JSON key, but it can work for simple tests.

Run this in PowerShell (replace the value with your API key):

```powershell
$env:GOOGLE_API_KEY = 'AIzaSyCuB3IMpCRLWioBF5l1ee6R6gpfiIPCS8w'
$env:PROVIDER = 'google'
```

Then run the ingest/chat commands as shown earlier. Reminder: do NOT commit this key into source control. Consider using a service-account JSON key and `GOOGLE_APPLICATION_CREDENTIALS` for production use.

Ingesting data from Postgres

You can ingest data from your Postgres DB into a local Chroma vector store. By default the loader expects a SQL query that returns two columns: `id` and `text`.

Example using your connection string (replace password/credentials if needed):

```powershell
python -m src.cli ingest --conn "postgresql://postgres:Anuj%402028@localhost:5432/arogya_swarm" --query "SELECT id, text FROM documents" --persist-dir ./vector_store
```

If your table or column names differ, pass a SQL query that returns `id` and `text` columns (alias if necessary).

Start chat (after ingest):

```powershell
python -m src.cli chat --persist-dir ./vector_store --k 4
```

Type messages at the prompt. Type `exit` or press Ctrl+C to quit.

Files

- `src/loader.py`: connect to Postgres and extract text rows
- `src/rag.py`: build vector store and retrieval chain
- `src/cli.py`: CLI entrypoints (`ingest`, `chat`)

Provided Postgres connection string (from user):

```
postgresql://postgres:Anuj%402028@localhost:5432/arogya_swarm
```

Security note: The connection string contains a password. Prefer setting it in environment variables or a secrets manager rather than committing it to disk.
