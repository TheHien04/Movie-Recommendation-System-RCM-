import { authHeaders } from './auth'
import { API_BASE } from './config'

const KEY = 'cinemate_ratings'

type RatingMap = Record<string, number>

function readLocal(): RatingMap {
  try {
    const raw = localStorage.getItem(KEY)
    return raw ? (JSON.parse(raw) as RatingMap) : {}
  } catch {
    return {}
  }
}

function writeLocal(map: RatingMap) {
  localStorage.setItem(KEY, JSON.stringify(map))
  window.dispatchEvent(new Event('cinemate:ratings'))
}

export function getLocalRating(title: string): number | null {
  const v = readLocal()[title]
  return v ? v : null
}

export function getAllLocalRatings(): RatingMap {
  return readLocal()
}

export async function setMovieRating(title: string, rating: number): Promise<void> {
  const map = readLocal()
  map[title] = rating
  writeLocal(map)

  const token = authHeaders().Authorization
  if (!token) return

  await fetch(`${API_BASE}/api/users/ratings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ movie_title: title, rating }),
  })
}

export async function syncRatingsFromCloud(): Promise<void> {
  const token = authHeaders().Authorization
  if (!token) return
  const res = await fetch(`${API_BASE}/api/users/ratings`, { headers: authHeaders() })
  if (!res.ok) return
  const data = (await res.json()) as { ratings: { movie_title: string; rating: number }[] }
  const map = readLocal()
  for (const r of data.ratings) map[r.movie_title] = r.rating
  writeLocal(map)
}
