import { authHeaders, getToken } from './auth'
import { API_BASE } from './config'
import { getCloudWatchlist, syncWatchlistCloud } from './api'

const STORAGE_KEY = 'cinemate-watchlist'
export const WATCHLIST_EVENT = 'cinemate-watchlist-updated'

export function getWatchlist(): string[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

export function isInWatchlist(title: string): boolean {
  return getWatchlist().includes(title)
}

function persist(titles: string[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(titles))
  window.dispatchEvent(new CustomEvent(WATCHLIST_EVENT, { detail: titles }))
}

export async function toggleWatchlist(title: string): Promise<boolean> {
  const list = getWatchlist()
  const adding = !list.includes(title)
  const next = adding ? [...list, title] : list.filter((t) => t !== title)
  persist(next)

  if (getToken()) {
    try {
      if (adding) {
        await fetch(`${API_BASE}/api/users/watchlist`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...authHeaders() },
          body: JSON.stringify({ title }),
        })
      } else {
        await fetch(`${API_BASE}/api/users/watchlist/${encodeURIComponent(title)}`, {
          method: 'DELETE',
          headers: authHeaders(),
        })
      }
    } catch {
      // offline-first: local list still valid
    }
  }

  return adding
}

/** Merge titles into watchlist (e.g. from share link). Returns count of new titles. */
export async function mergeWatchlistTitles(titles: string[]): Promise<number> {
  const list = getWatchlist()
  const merged = [...new Set([...list, ...titles.filter(Boolean)])]
  const added = merged.length - list.length
  if (added > 0) {
    persist(merged)
    if (getToken()) {
      try {
        await syncWatchlistCloud(merged)
      } catch {
        // local merge still valid
      }
    }
  }
  return added
}

export function encodeWatchlistShare(titles: string[]): string {
  return btoa(JSON.stringify(titles))
}

export function decodeWatchlistShare(encoded: string): string[] {
  try {
    const parsed = JSON.parse(atob(encoded))
    return Array.isArray(parsed) ? parsed.filter((t) => typeof t === 'string') : []
  } catch {
    return []
  }
}

/** Merge local + cloud watchlist after login */
export async function mergeWatchlistFromCloud(): Promise<string[]> {
  if (!getToken()) return getWatchlist()
  try {
    const { watchlist: cloud } = await getCloudWatchlist()
    const merged = [...new Set([...getWatchlist(), ...cloud])]
    persist(merged)
    await syncWatchlistCloud(merged)
    return merged
  } catch {
    return getWatchlist()
  }
}
