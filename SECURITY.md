# Security Policy

## Supported Versions
| Version | Supported |
|---------|-----------|
| main    | yes       |

## Reporting a Vulnerability
Email the maintainers or open a private security advisory on GitHub. Do not disclose critical issues publicly before a fix is available.

## Security Controls
- JWT authentication with expiry (`JWT_EXPIRY_HOURS`)
- Password policy: min 8 chars, at least one letter and one number
- API keys stored as SHA-256 hashes (plaintext shown once at creation)
- Admin endpoints require `X-Admin-Key` (`ADMIN_API_KEY`); admin UI keeps key in memory only
- Rate limiting on auth (`/api/auth/login`, `/api/auth/register`), `/recommend`, `/api/rag/chat`, B2B, TMDB proxy
- Failed login audit logging (`security.audit` logger)
- TMDB proxy allowlist for endpoint prefixes
- CORS restricted via `CORS_ORIGINS` (wildcard CORS disabled in production)
- Security headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Strict-Transport-Security` (prod), `Content-Security-Policy` (SPA)

## Production Checklist
- [x] Set strong `SECRET_KEY` and `ADMIN_API_KEY` (Render `generateValue` or manual)
- [x] Configure `CORS_ORIGINS` to your frontend domains only
- [ ] Use managed Postgres (`DATABASE_URL`), not SQLite
- [ ] Enable `SENTRY_DSN` for error tracking
- [ ] Never commit `.env` or `cinemate.db`
- [ ] Rotate API keys periodically
