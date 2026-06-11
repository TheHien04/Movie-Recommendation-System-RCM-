/** Production API host baked at build time; fallback if Render env was missing during static build. */
const RENDER_API_FALLBACK = 'https://movie-rcm-api.onrender.com'

function resolveApiBase(): string {
  const fromEnv = (import.meta.env.VITE_API_URL as string | undefined)?.trim()
  if (fromEnv) return fromEnv.replace(/\/$/, '')

  if (import.meta.env.PROD && typeof window !== 'undefined') {
    const host = window.location.hostname
    if (host === 'cinemate-web.onrender.com' || host.endsWith('.onrender.com')) {
      return RENDER_API_FALLBACK
    }
  }
  return ''
}

export const API_BASE = resolveApiBase()
