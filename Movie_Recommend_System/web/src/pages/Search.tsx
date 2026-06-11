import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Filter, Search as SearchIcon } from 'lucide-react'
import { fetchAdvancedSearch, fetchSearch, trackEvent } from '../lib/api'
import type { MovieSummary } from '../lib/api'
import { MovieCard } from '../components/MovieCard'

const GENRES = ['Action', 'Comedy', 'Drama', 'Horror', 'Romance', 'Sci-Fi', 'Thriller', 'Animation']

export function Search() {
  const [params, setParams] = useSearchParams()
  const [q, setQ] = useState(params.get('q') || '')
  const [genre, setGenre] = useState(params.get('genre') || '')
  const [minRating, setMinRating] = useState(Number(params.get('min_rating') || 0))
  const [yearFrom, setYearFrom] = useState(params.get('year_from') || '')
  const [showFilters, setShowFilters] = useState(false)
  const [results, setResults] = useState<MovieSummary[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    document.title = 'Search — Cinemate'
    const query = params.get('q')
    if (query || params.get('genre') || params.get('min_rating')) runSearch()
  }, [params])

  async function runSearch() {
    const query = params.get('q') || ''
    const g = params.get('genre') || ''
    const min = Number(params.get('min_rating') || 0)
    const yf = params.get('year_from') || ''
    const yt = params.get('year_to') || ''
    setLoading(true)
    try {
      const hasFilters = g || min > 0 || yf || yt
      if (hasFilters) {
        setResults(await fetchAdvancedSearch({
          q: query,
          genre: g || undefined,
          min_rating: min || undefined,
          year_from: yf ? Number(yf) : undefined,
          year_to: yt ? Number(yt) : undefined,
        }))
      } else if (query) {
        setResults(await fetchSearch(query))
      } else {
        setResults([])
      }
    } catch {
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    const next = new URLSearchParams()
    if (q.trim()) next.set('q', q.trim())
    if (genre) next.set('genre', genre)
    if (minRating > 0) next.set('min_rating', String(minRating))
    if (yearFrom) next.set('year_from', yearFrom)
    setParams(next)
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-6">
      <h1 className="text-4xl font-bold">Search Movies</h1>
      <p className="mt-2 text-white/60">Semantic search + advanced filters (genre, rating, year)</p>

      <form onSubmit={onSubmit} className="glass-panel mt-8 space-y-4 rounded-2xl p-4">
        <div className="flex gap-3">
          <SearchIcon className="mt-3 text-[#f5c518]" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search by title, genre, actor, plot..."
            className="flex-1 bg-transparent py-3 outline-none"
          />
          <button
            type="button"
            onClick={() => setShowFilters((v) => !v)}
            className={`inline-flex items-center gap-2 rounded-xl border px-4 py-2 text-sm ${
              showFilters ? 'border-[#f5c518]/50 text-[#f5c518]' : 'border-white/15'
            }`}
          >
            <Filter size={14} /> Filters
          </button>
          <button type="submit" className="rounded-xl bg-[#f5c518] px-6 font-semibold text-black">Search</button>
        </div>

        {showFilters && (
          <div className="grid gap-4 border-t border-white/10 pt-4 sm:grid-cols-3">
            <label className="block text-sm">
              <span className="text-white/50">Genre</span>
              <select
                value={genre}
                onChange={(e) => setGenre(e.target.value)}
                className="mt-1 w-full rounded-xl border border-white/10 bg-black/40 px-3 py-2"
              >
                <option value="">Any</option>
                {GENRES.map((g) => (
                  <option key={g} value={g.toLowerCase()}>{g}</option>
                ))}
              </select>
            </label>
            <label className="block text-sm">
              <span className="text-white/50">Min IMDb rating</span>
              <input
                type="number"
                min={0}
                max={10}
                step={0.5}
                value={minRating || ''}
                onChange={(e) => setMinRating(Number(e.target.value))}
                className="mt-1 w-full rounded-xl border border-white/10 bg-black/40 px-3 py-2"
                placeholder="e.g. 7.5"
              />
            </label>
            <label className="block text-sm">
              <span className="text-white/50">Year from</span>
              <input
                type="number"
                value={yearFrom}
                onChange={(e) => setYearFrom(e.target.value)}
                className="mt-1 w-full rounded-xl border border-white/10 bg-black/40 px-3 py-2"
                placeholder="e.g. 2010"
              />
            </label>
          </div>
        )}
      </form>

      {loading ? (
        <p className="mt-8 text-white/50">Searching...</p>
      ) : params.toString() && results.length === 0 ? (
        <div className="glass-panel mt-8 rounded-3xl p-10 text-center">
          <p className="text-lg text-white/80">No movies found</p>
          <p className="mt-2 text-white/50">Try AI Chat or Mood Discovery for broader picks</p>
        </div>
      ) : (
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {results.map((movie) => (
            <MovieCard
              key={movie.title}
              title={movie.title}
              poster={movie.poster}
              subtitle={movie.genre}
              rating={movie.imdb_rating}
              showQuickSave
              to={`/movie/${encodeURIComponent(movie.title)}`}
              onClick={() => trackEvent('search_click', movie.title)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
