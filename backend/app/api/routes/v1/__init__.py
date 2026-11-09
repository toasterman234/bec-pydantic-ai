"""API v1 router aggregation."""# ruff: noqa: I001 - Imports structured for Jinja2 template conditionals
from fastapi import APIRouter

from app.api.routes.v1 import healthfrom app.api.routes.v1 import admin_users, auth, usersfrom app.api.routes.v1 import oauthfrom app.api.routes.v1 import webhooksfrom app.api.routes.v1 import ragfrom app.api.routes.v1 import filesfrom app.api.routes.v1 import itemsfrom app.api.routes.v1 import admin_stats
v1_router = APIRouter()

# Health check routes (no auth required)
v1_router.include_router(health.router, tags=["health"])
# Authentication routes
v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# User routes
v1_router.include_router(users.router, prefix="/users", tags=["users"])
# OAuth2 routes
v1_router.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
# Webhook routes
v1_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
# RAG routes
v1_router.include_router(rag.router, prefix="/rag", tags=["rag"])
# File upload/download routes
v1_router.include_router(files.router, tags=["files"])
# Admin: user management + impersonation
v1_router.include_router(admin_users.router, prefix="/admin/users", tags=["admin:users"])v1_router.include_router(admin_stats.router, prefix="/admin", tags=["admin:stats"])
# Example Item CRUD (reference scaffold — safe to delete once you've added your own domain)
v1_router.include_router(items.router, prefix="/items", tags=["items"])