# Security

## Reporting a vulnerability

Email: **bencharney@yahoo.com** (or open a private security advisory on the repo). Please include:

- Affected version / commit
- Steps to reproduce
- Impact assessment (data exposure / privilege escalation / DoS / …)

We aim to acknowledge within 48h and ship a fix within 7 days for high-severity issues.

---

## Security model

### Authentication- **JWT (`HS256`)** signed with `SECRET_KEY`. Access token TTL = `ACCESS_TOKEN_EXPIRE_MINUTES` (default 30 min). Refresh token TTL = `REFRESH_TOKEN_EXPIRE_MINUTES` (default 7 days).
- **Password hashing:** bcrypt via `passlib`. Plain passwords never persisted.- **OAuth 2.0 (Google)** — auth-code flow. Token validated server-side, internal user record looked up/created by email.- **Stateless JWT** — no DB session table. Logout is client-side (drop tokens). For server-side revocation, regenerate with `--session-management`.
### Authorization

- **Role-based** via `RoleChecker` dep (`UserRole.USER` / `UserRole.ADMIN`).- **Admin pages** require `role=admin`. Sensitive ops (impersonate user, system-health) gated separately.
### Transport / network

- **CORS** — origin list from `settings.CORS_ORIGINS`. Restrict to your domains in production.
- **HTTPS** — enforce via reverse proxy (Nginx / Traefik / ALB). Strict-Transport-Security header set in middleware when `ENVIRONMENT=production`.
- **CSP** — frontend sets `frame-ancestors 'none'` by default to prevent click-jacking. See `frontend/next.config.ts` headers block.
### Data

- **Secrets** — read from environment via `pydantic-settings`. Never committed. See `.env.example` + `ENV_VARS.md`.- **RAG documents** — file uploads scoped per-org. No public read endpoint; all retrieval happens server-side during chat.
### Hardening checklist for production

- [ ] Rotate `SECRET_KEY` and `API_KEY` from generated defaults.
- [ ] Set `DEBUG=false` and `ENVIRONMENT=production`.
- [ ] Restrict `CORS_ORIGINS` to your domain(s).- [ ] Set `PROMETHEUS_AUTH_TOKEN` if `/metrics` is exposed on a public endpoint.- [ ] Enforce HTTPS at the proxy layer.
- [ ] Run `pip-audit` / `bun audit` in CI for dependency vulnerabilities.
- [ ] Configure database backups + restore test schedule.
## Known limitations

- **No 2FA / MFA** out of the box. Plan to add TOTP via `pyotp` — see `notes/thingstofix.md` §A.13.
- **No SAML / OIDC** beyond Google OAuth. Enterprise SSO needs custom IdP integration.
- **No automatic PII redaction** in logs — be careful what you log.- **No server-side session revocation** — JWTs valid until expiry. Compromised tokens require `SECRET_KEY` rotation (invalidates ALL sessions). Enable `--session-management` for selective revocation.