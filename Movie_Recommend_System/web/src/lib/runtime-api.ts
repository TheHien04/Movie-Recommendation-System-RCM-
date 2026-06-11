/** Live API — unified Render service (web + API same host) */
export const DEFAULT_LIVE_API = 'https://cinemate-live.onrender.com'

declare global {
  interface Window {
    __CINEMATE_API__?: string
  }
}

let resolved = ''

export function getApiBase(): string {
  if (resolved) return resolved
  if (typeof window !== 'undefined' && window.__CINEMATE_API__) {
    resolved = window.__CINEMATE_API__
    return resolved
  }

  if (typeof window !== 'undefined') {
    const host = window.location.hostname
    // Unified Render deploy: API is same origin
    if (host === 'cinemate-live.onrender.com') {
      resolved = window.location.origin
      return resolved
    }
    // GitHub Pages / other hosts → call unified API
    if (host.endsWith('.github.io') || host.endsWith('.onrender.com')) {
      resolved = DEFAULT_LIVE_API
      return resolved
    }
  }

  const fromEnv = (import.meta.env.VITE_API_URL as string | undefined)?.trim()
  if (fromEnv) {
    resolved = fromEnv.replace(/\/$/, '')
    return resolved
  }

  if (import.meta.env.DEV) return ''

  resolved = DEFAULT_LIVE_API
  return resolved
}

export async function initRuntimeApi(): Promise<string> {
  if (resolved) return resolved

  try {
    const res = await fetch(`${import.meta.env.BASE_URL}api-endpoint.txt`, { cache: 'no-store' })
    if (res.ok) {
      const url = (await res.text()).trim()
      if (url.startsWith('http')) {
        resolved = url.replace(/\/$/, '')
        window.__CINEMATE_API__ = resolved
        return resolved
      }
    }
  } catch {
    // ignore
  }

  resolved = getApiBase()
  if (resolved) window.__CINEMATE_API__ = resolved
  return resolved
}
