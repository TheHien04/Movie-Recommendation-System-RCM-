import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Play, Star, ExternalLink } from 'lucide-react'
import { fetchMovieDetails, fetchMovieExplain, fetchSimilar, trackEvent } from '../lib/api'
import type { MovieDetails } from '../lib/api'
import { SaveWatchlistButton } from '../components/SaveWatchlistButton'
import { MovieCard } from '../components/MovieCard'
import { StarRating } from '../components/StarRating'
import { ScoreBreakdown } from '../components/ScoreBreakdown'
import { addRecentView } from '../lib/history'

export function MovieDetail() {
  const { title = '' } = useParams()
  const decoded = decodeURIComponent(title)
  const [movie, setMovie] = useState<MovieDetails | null>(null)
  const [similar, setSimilar] = useState<{ title: string; score: number; poster?: string; imdb_rating?: number }[]>([])
  const [explain, setExplain] = useState<{ breakdown: Record<string, number>; hybrid_score: number | null; explanation: string } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    document.title = `${decoded} — Cinemate`
    setLoading(true)
    Promise.all([fetchMovieDetails(decoded), fetchSimilar(decoded), fetchMovieExplain(decoded).catch(() => null)])
      .then(([details, sim, exp]) => {
        setMovie(details)
        setSimilar(sim)
        setExplain(exp)
        addRecentView(details.title)
        trackEvent('view', details.title)
      })
      .catch(() => setMovie(null))
      .finally(() => setLoading(false))
  }, [decoded])

  if (loading) return <div className="p-20 text-center text-white/60">Loading...</div>
  if (!movie) return <div className="p-20 text-center">Movie not found. <Link to="/search" className="text-[#f5c518]">Search catalog</Link></div>

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-6">
      <div className="glass-panel grid gap-8 rounded-[2rem] p-8 lg:grid-cols-[280px_1fr]">
        <img src={movie.poster} alt={movie.title} className="w-full rounded-2xl object-cover" />
        <div className="space-y-4">
          <h1 className="text-4xl font-bold">{movie.title}</h1>
          <p className="text-white/70">{movie.overview}</p>
          <div className="flex flex-wrap gap-4 text-sm">
            <span className="text-[#f5c518] inline-flex items-center gap-1"><Star size={14} /> IMDb {movie.ratingIMDB}</span>
            <span>Genre: {movie.genre}</span>
            <span>Director: {movie.director}</span>
            <span>Runtime: {movie.runtime} min</span>
          </div>
          <StarRating title={movie.title} />
          <div className="flex flex-wrap gap-3">
            <SaveWatchlistButton title={movie.title} />
            {movie.trailer && (
              <a href={movie.trailer} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 rounded-full bg-[#f5c518] px-5 py-3 font-semibold text-black">
                <Play size={16} /> Trailer
              </a>
            )}
            {movie.affiliate_search && (
              <a href={movie.affiliate_search} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 rounded-full border border-[#f5c518]/40 px-5 py-3 text-[#f5c518]">
                <ExternalLink size={16} /> Where to Watch
              </a>
            )}
          </div>
          {movie.watch_providers && movie.watch_providers.length > 0 && (
            <div>
              <h3 className="mb-2 font-semibold">Streaming Providers</h3>
              <div className="flex flex-wrap gap-3">
                {movie.watch_providers.map((p) => (
                  <div key={`${p.name}-${p.type}`} className="flex items-center gap-2 rounded-xl bg-white/5 px-3 py-2 text-sm">
                    {p.logo && <img src={p.logo} alt={p.name} className="h-6 w-6 rounded" />}
                    {p.name} <span className="text-white/40">({p.type})</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {explain?.breakdown && Object.keys(explain.breakdown).length > 0 && (
        <section className="mt-12">
          <ScoreBreakdown breakdown={explain.breakdown} score={explain.hybrid_score} />
          {explain.explanation && <p className="mt-3 text-sm text-white/50">{explain.explanation}</p>}
        </section>
      )}

      {similar.length > 0 && (
        <section className="mt-12">
          <h2 className="mb-4 text-2xl font-bold">Similar Movies</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {similar.slice(0, 4).map((s) => (
              <MovieCard
                key={s.title}
                title={s.title}
                poster={s.poster}
                rating={s.imdb_rating}
                subtitle={`Similarity ${s.score.toFixed(3)}`}
                showQuickSave
                to={`/movie/${encodeURIComponent(s.title)}`}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
