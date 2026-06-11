# Security Policy

## Supported Versions
| Version | Supported |
|---------|-----------|
| main    | yes       |

## Reporting a Vulnerability
Email the maintainers or open a private security advisory on GitHub. Do not disclose critical issues publicly before a fix is available.

## Security Controls
- JWT authentication with expiry (`JWT_EXPIRY_HOURS`)
- API keys stored as SHA-256 hashes (plaintext shown once at creation)
- Admin endpoints require `X-Admin-Key` (`ADMIN_API_KEY`)
- Rate limiting on `/recommend`, `/api/rag/chat`, B2B, TMDB proxy
- TMDB proxy allowlist for endpoint prefixes
- CORS restricted via `CORS_ORIGINS`
- Security headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`

## Production Checklist
- [ ] Set strong `SECRET_KEY` and `ADMIN_API_KEY`
- [ ] Use managed Postgres (`DATABASE_URL`), not SQLite
- [ ] Configure `CORS_ORIGINS` to your frontend domain only
- [ ] Enable `SENTRY_DSN` for error tracking
- [ ] Never commit `.env` or `cinemate.db`
- [ ] Rotate API keys periodically
