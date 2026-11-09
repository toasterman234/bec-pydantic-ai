# bec_pydantic_ai

A FastAPI project

> Generated with [Full-Stack AI Agent Template](https://github.com/vstorm-co/full-stack-ai-agent-template).

---

## Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI + Pydantic v2 || **Database** | PostgreSQL (async via asyncpg) || **Auth** | JWT + refresh tokens + OAuth || **AI Framework** | pydantic_ai (openai) || **RAG** | pgvector vector store || **Frontend** | Next.js 15 + React 19 + Tailwind v4 |
---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| **Docker** | Desktop / Engine 24+ | <https://docs.docker.com/get-docker/> |
| **Make** | GNU Make 3.81+ (preinstalled on macOS/Linux) | Windows: install via [chocolatey](https://chocolatey.org/) `choco install make` or use WSL2 |
| **uv** | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` || **bun** | 1.x | `curl -fsSL https://bun.sh/install \| bash` (or use `npm` / `pnpm` if you prefer) |
> **Windows users:** the Makefile and shell helpers assume bash. Use **WSL2** or **Git Bash** for the smoothest experience. The Docker workflow below works identically on macOS, Linux, and WSL2.

---

## Quick Start (Local Dev)

### First time

```bash
make bootstrap       # = make dev + make seed
```

That's the only command you need on a fresh clone. After this, day-to-day is just `make dev`.

### Subsequent runs

```bash
make dev
```

`make dev` is **idempotent** — re-run it any time. It will:

1. Build the backend Docker image (cached after first run)
2. Start services via `docker-compose.dev.yml` (with hot-reload bind mounts)3. Poll Postgres until it accepts connections (`pg_isready` — no fixed sleeps)
4. Apply pending Alembic migrations (no-op if already at head)
It does **not** re-seed the admin user — that lives in `make seed` and is run once. This way `make dev` stays cheap to re-run after every code/config change.

**Then access:**

- API: <http://localhost:8000>
- Docs: <http://localhost:8000/docs>- Admin: <http://localhost:8000/admin> — `admin@example.com` / `admin123` after `make seed`- Frontend: <http://localhost:3000> — start with `make dev-frontend` (Docker) or `cd frontend && bun install && bun dev` (local)
### Day-to-day commands

```bash
make dev           # bootstrap or restart (idempotent, no admin re-seed)make seed          # one-shot admin creation (no-op if admin already exists)make dev-down      # stop everything
make dev-logs      # tail logs (Ctrl-C to exit)
make dev-rebuild   # force-rebuild backend image (after pyproject.toml change)make dev-frontend  # start the Next.js container```

If you prefer running the backend on the host (not in Docker) — useful for breakpoints / IDE debugging:

```bash
make install       # uv sync + pre-commit install
docker compose -f docker-compose.dev.yml up -d db milvus etcd miniomake db-upgrade    # apply migrations
make run           # run uvicorn locally with --reload
```

---

## Environments

| `make` target | Compose file | Use case |
|---|---|---|
| `make dev` | `docker-compose.dev.yml` | Local development with hot-reload + bind-mounted source. |
| `make stage` | `docker-compose.yml` | Production-like build, no bind mounts, runs on localhost. Good for sanity-checking before deploy. |
| `make prod` | `docker-compose.prod.yml` | Production. Requires `backend/.env` (copy from `backend/.env.example`, fill real secrets) and an external Nginx using `nginx/nginx.conf`. |

Each env has matching `-down`, `-logs`, `-rebuild` siblings (e.g. `make stage-down`).

---

## Project Structure

```
backend/app/
├── main.py               # FastAPI app + lifespan
├── api/
│   ├── deps.py           # Annotated DI aliases (DBSession, CurrentUser, *Svc)
│   ├── exception_handlers.py
│   └── routes/v1/        # HTTP endpoints — call services, never repos
├── core/
│   ├── config.py         # pydantic-settings (reads .env)
│   ├── security.py       # JWT, bcrypt, API key verification
│   ├── exceptions.py     # AppException → NotFound / Auth / etc.
│   └── middleware.py
├── db/
│   ├── base.py           # DeclarativeBase + TimestampMixin
│   └── models/           # SQLAlchemy models (Mapped[] type hints)
├── schemas/              # Pydantic v2: *Create / *Update / *Read / *List
├── repositories/         # Data access — db.flush() never commit
├── services/             # Business logic — raises domain exceptions
├── agents/               # AI agent wrappers + tools├── rag/                  # RAG: vectorstore + embeddings + ingestion + sources
│   └── connectors/       # Pluggable sync sources (Google Drive, S3, …)└── commands/             # Click CLI commands (auto-discovered by `bec_pydantic_ai cmd …`)
frontend/src/
├── app/
│   ├── [locale]/         # next-intl routes (en/pl)│   │   └── (dashboard)/  # Authenticated app
│   └── api/              # Server-side API proxies (forward auth cookies)
├── components/           # React components (chat, marketing, ui primitives)
├── hooks/                # useAuth, useChat, useConversations, …
├── stores/               # Zustand stores
└── lib/                  # api-client, server-api, utils```

---

## CLI

The generated project ships a Click CLI exposed as `bec_pydantic_ai` (after `make install`):

```bash
bec_pydantic_ai server run --reload          # dev server
bec_pydantic_ai db upgrade                   # apply migrations
bec_pydantic_ai db migrate -m "message"      # create new migration
bec_pydantic_ai user create-admin            # interactive admin creationbec_pydantic_ai rag-ingest <path> -c docs    # ingest local files
bec_pydantic_ai rag-search "query" -c docs   # semantic search
bec_pydantic_ai rag-collections              # list collections```

Run `make help` for a categorized list, or `bec_pydantic_ai --help` for full CLI docs.

---

## Configuration

All backend config lives in `backend/.env` (committed for dev defaults). Key variables:

```bashPOSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=bec_pydantic_ai
# OpenAI — required for chat + embeddings
OPENAI_API_KEY=sk-…
# Google OAuth (Sign in with Google)
GOOGLE_CLIENT_ID=…
GOOGLE_CLIENT_SECRET=…```

See `backend/.env.example` for the full list with comments.

For production, **never** commit secrets — `backend/.env` is gitignored. Fill it with real values on the server (or inject them via your platform's secret manager: Doppler, AWS Secrets Manager, GitHub Actions secrets, etc.). The same `backend/.env` is used for dev and prod — there is no separate `.env.prod`.

---

## Development

| Command | What it does |
|---|---|
| `make test` | Run pytest |
| `make lint` | Run ruff check + format check + ty |
| `make format` | Auto-format with ruff || `make db-migrate` | Generate a new migration from model changes (interactive) |
| `make db-upgrade` | Apply pending migrations |
| `make db-downgrade` | Roll back one migration |
| `make db-current` | Show current head || `make create-admin` | Interactive admin creation |
| `make user-list` | List all users |
---
## RAG (Knowledge Base)

Using **pgvector** as the vector store with **openai** embeddings.

```bash
# Ingest local files (recursive)
bec_pydantic_ai rag-ingest /path/to/docs/ --collection documents --recursive
# Semantic search
bec_pydantic_ai rag-search "your query" --collection documents
```

PDF parsing uses **all**. See `docs/howto/add-rag-source.md` to add a new source connector.
---

## Frontend

```bash
cd frontend
bun install
bun dev          # http://localhost:3000
bun run lint
bun run build
```

The frontend talks to the backend through Next.js API route handlers in `src/app/api/*` (server-side proxy that forwards auth cookies to the FastAPI backend). Direct calls to `localhost:8000` from the browser are deliberately avoided.

i18n (PL + EN) ships out of the box via `next-intl`. Add a new locale by extending `messages/<lang>.json` and `src/i18n.ts`.
---

## Deployment

### Frontend → Vercel

```bash
cd frontend && npx vercel --prod
```

Set in the Vercel dashboard:

- `BACKEND_URL` = `https://api.your-domain.com`
- `BACKEND_WS_URL` = `wss://api.your-domain.com`
- `NEXT_PUBLIC_AUTH_ENABLED` = `true`- `NEXT_PUBLIC_RAG_ENABLED` = `true`
### Backend → your server

```bash
# 1. SSH to the box, clone the repo
# 2. cp backend/.env.example backend/.env, fill in real secrets
# 3. Configure nginx using nginx/nginx.conf as reference
# 4. Bring up the stack:
make prod

# Day-to-day:
make prod-logs
make prod-down
```

Migrations run automatically on `make prod`. For a fresh deploy on a new host, the same `make prod` is the bootstrap command.

---

## Guides

| Guide | What |
|-------|-------|
| `docs/howto/add-api-endpoint.md` | Add a new REST endpoint |
| `docs/howto/add-agent-tool.md` | Create an agent tool |
| `docs/howto/customize-agent-prompt.md` | Tune system prompts || `docs/howto/add-rag-source.md` | Add a RAG document source |
| `docs/howto/add-sync-connector.md` | Build a custom sync connector |
---

*Generated with [Full-Stack AI Agent Template](https://github.com/vstorm-co/full-stack-ai-agent-template) v.*
