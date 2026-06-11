/** Live Render API — must match render.yaml service name cinemate-rcm-api */
export const RENDER_LIVE_API = 'https://cinemate-rcm-api.onrender.com'

function resolveApiBase(): string {
  if (typeof window !== 'undefined') {
    const host = window.location.hostname
    // Any Render frontend → always use dedicated API service (static site has no /api routes)
    if (host.endsWith('.onrender.com')) {
      return RENDER_LIVE_API
    }
  }

  const fromEnv = (import.meta.env.VITE_API_URL as string | undefined)?.trim()
  if (fromEnv) return fromEnv.replace(/\/$/, '')

  return ''
}

export const API_BASE = resolveApiBase()
