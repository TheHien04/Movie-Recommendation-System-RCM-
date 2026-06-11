import { authHeaders } from './auth'
import { API_BASE } from './config'

export type MovieSummary = {
  title: string
  poster?: string
  genre?: string
  actors?: string
  imdb_rating?: number
  rotten_rating?: number
  description?: string
  year?: number | string
  director?: string
  score?: number
  personalized?: boolean
  explanation?: string
  source?: string
}

export type Recommendation = {
  title: string
  poster?: string
  total_rating?: number
  score?: number
  explanation?: string
}

export type WatchProvider = { name: string; type: string; logo?: string }

export type MovieDetails = {
  title: string
  overview?: string
  ratingIMDB?: number
  ratingRotten?: number
  ratingTMDB?: number
  poster?: string
  actors?: string
  director?: string
  runtime?: number | string
  genre?: string
  year?: number | string
  trailer?: string | null
  watch_providers?: WatchProvider[]
  affiliate_search?: string
}

async function request<T>(path: string, init?: RequestInit, attempt = 0): Promise<T> {
  const controller = new AbortController()
  const timeoutMs =
    typeof window !== 'undefined' && window.location.hostname.endsWith('.onrender.com') ? 90_000 : 30_000
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
        ...(init?.headers || {}),
      },
    })
    if (!res.ok) throw new Error(`Request failed: ${res.status}`)
    return res.json()
  } catch (err) {
    if (attempt < 1 && typeof window !== 'undefined' && window.location.hostname.endsWith('.onrender.com')) {
      await new Promise((r) => setTimeout(r, 3000))
      return request<T>(path, init, attempt + 1)
    }
    throw err
  } finally {
    clearTimeout(timer)
  }
}

export const fetchRandomMovies = () => request<{ movies: MovieSummary[] }>('/random_movies').then((d) => d.movies)
export const fetchGenres = () => request<{ genres: { name: string; movies: MovieSummary[] }[] }>('/api/genres').then((d) => d.genres)
export const fetchTrending = () => request<{ trending: MovieSummary[] }>('/api/trending').then((d) => d.trending)
export const fetchPersonalized = () => request<{ movies: MovieSummary[] }>('/api/personalized').then((d) => d.movies)
export const fetchSearch = (q: string) => request<{ results: MovieSummary[] }>(`/api/search?q=${encodeURIComponent(q)}`).then((d) => d.results)

export async function fetchAdvancedSearch(params: {
  q?: string
  genre?: string
  min_rating?: number
  year_from?: number
  year_to?: number
}) {
  const sp = new URLSearchParams()
  if (params.q) sp.set('q', params.q)
  if (params.genre) sp.set('genre', params.genre)
  if (params.min_rating) sp.set('min_rating', String(params.min_rating))
  if (params.year_from) sp.set('year_from', String(params.year_from))
  if (params.year_to) sp.set('year_to', String(params.year_to))
  return request<{ results: MovieSummary[] }>(`/api/search/advanced?${sp}`).then((d) => d.results)
}

export const fetchMoods = () =>
  request<{ moods: { id: string; label: string; query: string }[] }>('/api/moods').then((d) => d.moods)

export const fetchMoodRecommend = (moodId: string) =>
  request<{ recommended_movies: Recommendation[]; label: string; query: string }>(
    `/api/moods/${encodeURIComponent(moodId)}/recommend`,
  )

export async function compareMovies(titles: string[]) {
  return request<{ movies: MovieDetails[]; similarity_matrix: number[][]; engine: string }>('/api/compare', {
    method: 'POST',
    body: JSON.stringify({ titles }),
  })
}

export async function fetchMovieExplain(title: string) {
  return request<{
    title: string
    hybrid_score: number | null
    breakdown: Record<string, number>
    explanation: string
    similar_in_ranking: string[]
  }>(`/api/ml/explain/${encodeURIComponent(title)}`)
}

export async function fetchRecentViews() {
  return request<{ titles: string[] }>('/api/events/recent?limit=12').then((d) => d.titles)
}

export const fetchPublicStats = () => request<Record<string, unknown>>('/api/stats/public')

export const fetchLeaderboard = (genre?: string) => {
  const q = genre ? `?genre=${encodeURIComponent(genre)}` : ''
  return request<{ movies: MovieSummary[] }>(`/api/leaderboard${q}`).then((d) => d.movies)
}

export async function fetchAdminDashboard(adminKey: string) {
  const res = await fetch(`${API_BASE}/api/admin/dashboard`, {
    headers: { 'X-Admin-Key': adminKey },
  })
  if (!res.ok) throw new Error('Admin request failed')
  return res.json()
}
export const fetchSimilar = (title: string) =>
  request<{ similar: { title: string; score: number; poster?: string; imdb_rating?: number }[] }>(
    `/api/ml/similar/${encodeURIComponent(title)}`,
  ).then((d) => d.similar)
export const fetchMovieDetails = (title: string) => request<MovieDetails>(`/movie/${encodeURIComponent(title)}`)

export async function fetchMoviesBatch(titles: string[]) {
  return request<{ movies: MovieSummary[] }>('/api/movies/batch', {
    method: 'POST',
    body: JSON.stringify({ titles }),
  }).then((d) => d.movies)
}
export const fetchMlInfo = () => request<Record<string, unknown>>('/api/ml/info')
export const fetchHealth = () => request<Record<string, unknown>>('/api/health')
export const fetchApiDocs = () => request<Record<string, unknown>>('/api/docs')
export const fetchFeedbackStats = () => request<Record<string, unknown>>('/api/feedback/stats')

export async function fetchRecommendations(query: string, mode?: 'rag' | 'hybrid') {
  return request<{
    recommended_movies: Recommendation[]
    model: string
    variant?: string
    answer?: string
    engines: Record<string, string>
  }>('/recommend', {
    method: 'POST',
    body: JSON.stringify({ query, mode: mode === 'rag' ? 'rag' : undefined, variant: mode === 'rag' ? 'B' : 'A' }),
  })
}

export async function fetchRagChat(query: string) {
  return request<{ answer: string; recommended_movies: Recommendation[]; model: string; variant: string }>(
    '/api/rag/chat',
    { method: 'POST', body: JSON.stringify({ query, mode: 'rag' }) },
  )
}

export async function submitFeedback(movie_title: string, rating: 1 | -1, query?: string, variant?: string) {
  return request('/api/feedback', {
    method: 'POST',
    body: JSON.stringify({ movie_title, rating, query, variant }),
  })
}

export async function trackEvent(event_type: string, movie_title?: string) {
  return request('/api/events', {
    method: 'POST',
    body: JSON.stringify({ event_type, movie_title }),
  })
}

export async function login(email: string, password: string) {
  return request<{ token: string; user: { id: number; email: string; display_name: string } }>(
    '/api/auth/login',
    { method: 'POST', body: JSON.stringify({ email, password }) },
  )
}

export async function register(email: string, password: string, display_name?: string) {
  return request<{ token: string; user: { id: number; email: string; display_name: string } }>(
    '/api/auth/register',
    { method: 'POST', body: JSON.stringify({ email, password, display_name }) },
  )
}

export async function fetchProfile() {
  return request<{ user: { id: number; email: string; display_name: string }; stats: { watchlist: number; chat_messages: number } }>(
    '/api/users/profile',
  )
}

export async function syncWatchlistCloud(titles: string[]) {
  return request('/api/users/watchlist/sync', { method: 'POST', body: JSON.stringify({ titles }) })
}

export async function getCloudWatchlist() {
  return request<{ watchlist: string[] }>('/api/users/watchlist')
}
