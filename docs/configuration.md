# Configuration Reference

All configuration is managed via environment variables, loaded from
`backend/.env` using [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).

Settings are defined in `app/core/config.py` and accessed via the global
`settings` object:

```python
from app.core.config import settings

print(settings.AI_MODEL)
print(settings.DEBUG)
```

## Getting Started

```bash
cd backend

# Copy the example file (may already exist if generated with --generate-env)
cp .env.example .env

# Generate a secure secret key
openssl rand -hex 32
# Paste the output as SECRET_KEY in .env
```

## Project Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `PROJECT_NAME` | `bec_pydantic_ai` | Display name for the project |
| `API_V1_STR` | `/api/v1` | API version prefix |
| `DEBUG` | `false` | Enable debug mode (verbose errors, auto-reload) |
| `ENVIRONMENT` | `local` | One of: `development`, `local`, `staging`, `production` |
| `TIMEZONE` | `` | IANA timezone (e.g. `UTC`, `Europe/Warsaw`, `America/New_York`) |
| `MODELS_CACHE_DIR` | `./models_cache` | Directory for cached ML models |
| `MEDIA_DIR` | `./media` | Directory for uploaded files |
| `MAX_UPLOAD_SIZE_MB` | `50` | Maximum file upload size in megabytes |
## Authentication

### JWT

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | (insecure default) | JWT signing key. **Must** be changed in production. Generate with: `openssl rand -hex 32` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | `10080` | Refresh token lifetime (7 days) |
| `ALGORITHM` | `HS256` | JWT signing algorithm |

Production validation: `SECRET_KEY` must be at least 32 characters and cannot
use the default value in `ENVIRONMENT=production`.
### OAuth2 (Google)

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_CLIENT_ID` | (empty) | Google OAuth2 client ID |
| `GOOGLE_CLIENT_SECRET` | (empty) | Google OAuth2 client secret |
| `GOOGLE_REDIRECT_URI` | `http://localhost:8000/api/v1/oauth/google/callback` | OAuth2 callback URL |
| `FRONTEND_URL` | `http://localhost:3000` | Frontend URL for OAuth2 redirects |
## Database (PostgreSQL)

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_HOST` | `localhost` | PostgreSQL host |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_USER` | `postgres` | PostgreSQL user |
| `POSTGRES_PASSWORD` | (empty) | PostgreSQL password |
| `POSTGRES_DB` | `bec_pydantic_ai` | Database name |
| `DB_POOL_SIZE` | `5` | Connection pool size |
| `DB_MAX_OVERFLOW` | `10` | Max overflow connections |
| `DB_POOL_TIMEOUT` | `30` | Pool timeout in seconds |

Computed properties:
- `DATABASE_URL` -- async connection string (`postgresql+asyncpg://...`)
- `DATABASE_URL_SYNC` -- sync connection string for Alembic
## AI Agent

| Variable | Default | Description |
|----------|---------|-------------|| `OPENAI_API_KEY` | (empty) | OpenAI API key |
| `AI_MODEL` | `gpt-5.5` | Default LLM model for chat || `AI_TEMPERATURE` | `0.7` | LLM temperature (0.0 = deterministic, 1.0 = creative) |
| `AI_AVAILABLE_MODELS` | (auto-configured) | JSON list of models shown in the UI model selector |
| `AI_FRAMEWORK` | `pydantic_ai` | AI framework (informational) |
| `LLM_PROVIDER` | `openai` | LLM provider (informational) |

### Customizing Available Models

Override `AI_AVAILABLE_MODELS` in `.env` to customize the model selector:

```bash
AI_AVAILABLE_MODELS=["gpt-5.5","gpt-5.4","claude-opus-4-7"]
```
## Observability (Logfire)

| Variable | Default | Description |
|----------|---------|-------------|
| `LOGFIRE_TOKEN` | (none) | Pydantic Logfire token. Get one at https://logfire.pydantic.dev |
| `LOGFIRE_SERVICE_NAME` | `bec_pydantic_ai` | Service name in Logfire dashboard |
| `LOGFIRE_ENVIRONMENT` | `development` | Environment tag |
## RAG (Retrieval Augmented Generation)

### Vector Database
pgvector uses the existing PostgreSQL connection. No additional configuration
is needed.
### Embeddings

| Variable | Default | Description |
|----------|---------|-------------|| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
### Chunking & Retrieval

| Variable | Default | Description |
|----------|---------|-------------|
| `RAG_CHUNK_SIZE` | `512` | Maximum characters per chunk |
| `RAG_CHUNK_OVERLAP` | `50` | Characters of overlap between chunks |
| `RAG_CHUNKING_STRATEGY` | `recursive` | Chunking strategy: `recursive`, `markdown`, `fixed` |
| `RAG_DEFAULT_COLLECTION` | `documents` | Default collection for search (used by agent tool) |
| `RAG_TOP_K` | `10` | Default number of results to return |
| `RAG_HYBRID_SEARCH` | `false` | Enable BM25 + vector hybrid search |
| `RAG_ENABLE_OCR` | `false` | OCR fallback for scanned PDFs (requires `tesseract-ocr`) |

### Document Parsing
| Variable | Default | Description |
|----------|---------|-------------|
| `PDF_PARSER` | `pymupdf` | PDF parser for RAG ingestion: `pymupdf`, `llamaparse`, `liteparse` |
| `CHAT_PDF_PARSER` | `pymupdf` | PDF parser for chat file uploads: `pymupdf`, `llamaparse`, `liteparse` |
| `LLAMAPARSE_API_KEY` | (empty) | LlamaParse API key (required for `llamaparse` parser) |
| `LLAMAPARSE_TIER` | `agentic` | LlamaParse tier: `fast`, `cost_effective`, `agentic`, `agentic_plus` |
## CORS

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `["http://localhost:3000","http://localhost:8080"]` | Allowed origins (JSON array) |
| `CORS_ALLOW_CREDENTIALS` | `true` | Allow credentials (cookies) |
| `CORS_ALLOW_METHODS` | `["*"]` | Allowed HTTP methods |
| `CORS_ALLOW_HEADERS` | `["*"]` | Allowed HTTP headers |

Production validation: `CORS_ORIGINS` cannot contain `"*"` in
`ENVIRONMENT=production`.
## Prometheus

| Variable | Default | Description |
|----------|---------|-------------|
| `PROMETHEUS_METRICS_PATH` | `/metrics` | Metrics endpoint path |
| `PROMETHEUS_INCLUDE_IN_SCHEMA` | `false` | Include metrics endpoint in OpenAPI schema |
## File Storage (S3/MinIO)

| Variable | Default | Description |
|----------|---------|-------------|
| `S3_ENDPOINT` | (none) | S3/MinIO endpoint URL |
| `S3_ACCESS_KEY` | (empty) | Access key |
| `S3_SECRET_KEY` | (empty) | Secret key |
| `S3_BUCKET` | `bec_pydantic_ai` | Bucket name |
| `S3_REGION` | `us-east-1` | AWS region |
## Docker / Production

| Variable | Default | Description |
|----------|---------|-------------|
| `DOMAIN` | `example.com` | Production domain (for Traefik) |
| `ACME_EMAIL` | `admin@example.com` | Let's Encrypt email for SSL certs |
## Production Checklist

Before deploying to production, ensure these variables are properly set:1. `SECRET_KEY` -- Generate a unique 64-character hex key: `openssl rand -hex 32`3. `ENVIRONMENT` -- Set to `production`
4. `DEBUG` -- Set to `false`5. `POSTGRES_PASSWORD` -- Use a strong, unique password6. `CORS_ORIGINS` -- List only your actual frontend domain(s)8. `OPENAI_API_KEY` -- Your production API key