"""FastAPI application entry point."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanagerfrom typing import TypedDict
logger = logging.getLogger(__name__)

from fastapi import FastAPIfrom fastapi_pagination import add_pagination
from app.api.exception_handlers import register_exception_handlers
from app.api.router import api_router
from app.core.config import settingsfrom app.core.logfire_setup import instrument_app, setup_logfirefrom app.core.logging import setup_logging
from app.core.middleware import RequestIDMiddlewarefrom app.services.rag.embeddings import EmbeddingServicefrom app.services.rag.vectorstore import PgVectorStorefrom app.services.rag.vectorstore import BaseVectorStore

class LifespanState(TypedDict, total=False):
    """Lifespan state - resources available via request.state."""    embedding_service: EmbeddingService
    vector_store: BaseVectorStore

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[LifespanState, None]:
    """Application lifespan - startup and shutdown events.

    Resources yielded here are available via request.state in route handlers.
    See: https://asgi.readthedocs.io/en/latest/specs/lifespan.html#lifespan-state
    """
    # === Startup ===    state: LifespanState = {}    setup_logfire()    from app.core.logfire_setup import instrument_asyncpg
    instrument_asyncpg()    from app.core.logfire_setup import instrument_pydantic_ai
    instrument_pydantic_ai()    from app.core.config import settings
    try:
        embedder = EmbeddingService(settings=settings.rag)
        embedder.warmup()
        state["embedding_service"] = embedder
    except Exception as e:
        logger.error(f"Embedding service warmup failed: {e}. RAG will not be available.")    if "embedding_service" in state:
        try:
            vector_store = PgVectorStore(settings=settings.rag, embedding_service=embedder)
            state["vector_store"] = vector_store
        except Exception as e:
            logger.error(f"pgvector connection failed: {e}. Vector store will not be available.")    yield state
    # === Shutdown ===    from app.db.session import close_db
    await close_db()    try:
        if "vector_store" in state:
            await state["vector_store"].engine.dispose()  # type: ignore[attr-defined]
    except Exception:
        pass

# Environments where API docs should be visible
SHOW_DOCS_ENVIRONMENTS = ("local", "staging", "development")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Only show docs in allowed environments (hide in production)
    show_docs = settings.ENVIRONMENT in SHOW_DOCS_ENVIRONMENTS
    openapi_url = f"{settings.API_V1_STR}/openapi.json" if show_docs else None
    docs_url = "/docs" if show_docs else None
    redoc_url = "/redoc" if show_docs else None

    # OpenAPI tags for better documentation organization
    openapi_tags = [
        {
            "name": "health",
            "description": "Health check endpoints for monitoring and Kubernetes probes",
        },        {
            "name": "auth",
            "description": "Authentication endpoints - login, register, token refresh",
        },
        {
            "name": "users",
            "description": "User management endpoints",
        },        {
            "name": "oauth",
            "description": "OAuth2 social login endpoints (Google, etc.)",
        },        {
            "name": "webhooks",
            "description": "Webhook management - subscribe to events and manage deliveries",
        },        {
            "name": "websocket",
            "description": "WebSocket endpoints for real-time communication",
        },        {
            "name": "rag",
            "description": "Retrieval Augmented Generation endpoints",
        },    ]

    # PII redaction in logs (GDPR/compliance)
    setup_logging()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        summary="FastAPI application with Logfire observability",
        description="""
A FastAPI project

## Features- **Authentication**: JWT-based authentication with refresh tokens- **Database**: Async database operations- **AI Agent**: PydanticAI-powered conversational assistant- **Observability**: Logfire integration for tracing and monitoring- **RAG**: Retrieval Augmented Generation with Milvus and LangChain
## Documentation

- [Swagger UI](/docs) - Interactive API documentation
- [ReDoc](/redoc) - Alternative documentation view
        """.strip(),
        version="0.1.0",
        openapi_url=openapi_url,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_tags=openapi_tags,
        contact={
            "name": "Bec",
            "email": "bencharney@yahoo.com",
        },
        license_info={
            "name": "MIT",
            "identifier": "MIT",
        },
        lifespan=lifespan,
    )    # Logfire instrumentation. setup_logfire() is also called from the lifespan
    # for the runtime app, but we call it here too so that import-time test
    # clients (which never run lifespan) silence the "configure first" warning.
    setup_logfire()
    instrument_app(app)
    # Request ID middleware (for request correlation/debugging)
    app.add_middleware(RequestIDMiddleware)

    # Exception handlers
    register_exception_handlers(app)
    # CORS middleware
    from starlette.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    # Prometheus metrics
    from prometheus_fastapi_instrumentator import Instrumentator

    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/health", "/health/ready", "/health/live", settings.PROMETHEUS_METRICS_PATH],
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )
    # Optional Bearer-token guard so the metrics endpoint can be exposed on a
    # public ingress without leaking internals. When PROMETHEUS_AUTH_TOKEN is
    # empty the endpoint is unauthenticated (typical for private networks).
    if settings.PROMETHEUS_AUTH_TOKEN:
        from fastapi import Depends, Header, HTTPException, status as http_status

        def _verify_metrics_token(authorization: str = Header(default="")) -> None:
            expected = f"Bearer {settings.PROMETHEUS_AUTH_TOKEN}"
            import secrets as _secrets
            if not _secrets.compare_digest(authorization, expected):
                raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED)

        instrumentator.instrument(app).expose(
            app,
            endpoint=settings.PROMETHEUS_METRICS_PATH,
            include_in_schema=settings.PROMETHEUS_INCLUDE_IN_SCHEMA,
            dependencies=[Depends(_verify_metrics_token)],
        )
    else:
        instrumentator.instrument(app).expose(
            app,
            endpoint=settings.PROMETHEUS_METRICS_PATH,
            include_in_schema=settings.PROMETHEUS_INCLUDE_IN_SCHEMA,
        )
    # Session middleware (for admin authentication and/or OAuth)
    from starlette.middleware.sessions import SessionMiddleware
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
    # Admin panel (environment restricted)    ADMIN_ALLOWED_ENVIRONMENTS = ["development", "local", "staging"]
    if settings.ENVIRONMENT in ADMIN_ALLOWED_ENVIRONMENTS:
        from app.admin import setup_admin
        setup_admin(app)
    # API Version Deprecation (uncomment when deprecating old versions)
    # Example: Mark v1 as deprecated when v2 is ready
    # from app.api.versioning import VersionDeprecationMiddleware
    # app.add_middleware(
    #     VersionDeprecationMiddleware,
    #     deprecated_versions={
    #         "v1": {
    #             "sunset": "2025-12-31",
    #             "link": "/docs/migration/v2",
    #             "message": "Please migrate to API v2",
    #         }
    #     },
    # )

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    # Pagination
    add_pagination(app)
    return app


app = create_app()
