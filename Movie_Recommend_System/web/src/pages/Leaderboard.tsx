import { useEffect, useState } from 'react'
import { Trophy } from 'lucide-react'
import { fetchLeaderboard } from '../lib/api'
import type { MovieSummary } from '../lib/api'
import { MovieCard } from '../components/MovieCard'
import { MovieRailSkeleton } from '../components/LoadingSkeleton'

const GENRES = ['', 'action', 'comedy', 'drama', 'horror', 'romance', 'sci-fi', 'thriller', 'animation']

export function Leaderboard() {
  const [genre, setGenre] = useState('')
  const [movies, setMovies] = useState<MovieSummary[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    document.title = 'Leaderboard — Cinemate'
    setLoading(true)
    fetchLeaderboard(genre || undefined)
      .then(setMovies)
      .catch(() => setMovies([]))
      .finally(() => setLoading(false))
  }, [genre])

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-6">
      <div className="flex items-center gap-3">
        <Trophy className="text-[#f5c518]" size={32} />
        <div>
          <h1 className="text-4xl font-bold">IMDb Leaderboard</h1>
          <p className="mt-1 text-white/60">Top-rated movies in the catalog — filter by genre</p>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        {GENRES.map((g) => (
          <button
            key={g || 'all'}
            type="button"
            onClick={() => setGenre(g)}
            className={`rounded-full px-4 py-2 text-sm capitalize transition ${
              genre === g ? 'bg-[#f5c518] text-black font-semibold' : 'border border-white/15 hover:bg-white/5'
            }`}
          >
            {g || 'All genres'}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="mt-8"><MovieRailSkeleton count={8} /></div>
      ) : (
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {movies.map((movie, i) => (
            <div key={movie.title} className="relative">
              <span className="absolute -left-2 -top-2 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-[#f5c518] text-sm font-bold text-black">
                {i + 1}
              </span>
              <MovieCard
                title={movie.title}
                poster={movie.poster}
                subtitle={movie.genre}
                rating={movie.imdb_rating}
                showQuickSave
                to={`/movie/${encodeURIComponent(movie.title)}`}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
