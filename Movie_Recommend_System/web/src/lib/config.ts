/**
 * API base URL.
 * - Local dev: empty → Vite proxy to :5001
 * - Render unified deploy: empty → same origin (Flask serves web + API)
 */
function resolveApiBase(): string {
  const fromEnv = (import.meta.env.VITE_API_URL as string | undefined)?.trim()
  if (fromEnv) {
    const base = fromEnv.replace(/\/$/, '')
    // Ignore stale builds pointing at old/broken API hosts
    if (base.includes('cinemate-api.onrender.com')) {
      return typeof window !== 'undefined' ? window.location.origin : ''
    }
    return base
  }

  if (import.meta.env.PROD && typeof window !== 'undefined') {
    if (window.location.hostname.endsWith('.onrender.com')) {
      return window.location.origin
    }
  }
  return ''
}

export const API_BASE = resolveApiBase()
