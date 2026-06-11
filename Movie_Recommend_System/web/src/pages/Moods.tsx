import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Heart, Sparkles, Zap, Ghost, Brain, Trophy, Clock, Coffee } from 'lucide-react'
import { fetchMoodRecommend, fetchMoods } from '../lib/api'
import type { MovieSummary } from '../lib/api'
import { MovieCard } from '../components/MovieCard'
import { MovieRailSkeleton } from '../components/LoadingSkeleton'

const ICONS: Record<string, typeof Heart> = {
  happy: Sparkles,
  romantic: Heart,
  thrilling: Zap,
  scared: Ghost,
  'mind-bending': Brain,
  inspiring: Trophy,
  nostalgic: Clock,
  cozy: Coffee,
}

export function Moods() {
  const [moods, setMoods] = useState<{ id: string; label: string; query: string }[]>([])
  const [active, setActive] = useState<string | null>(null)
  const [movies, setMovies] = useState<MovieSummary[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    document.title = 'Mood Discovery — Cinemate'
    fetchMoods().then(setMoods).catch(() => setMoods([]))
  }, [])

  async function pickMood(id: string) {
    setActive(id)
    setLoading(true)
    try {
      const data = await fetchMoodRecommend(id)
      setMovies(data.recommended_movies as MovieSummary[])
    } catch {
      setMovies([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-6">
      <h1 className="text-4xl font-bold">Mood Discovery</h1>
      <p className="mt-2 max-w-2xl text-white/60">
        Pick how you feel — Hybrid v3 maps your mood to semantic queries and ranks the catalog with
        Transformer + SVD + NeuMF fusion.
      </p>

      <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {moods.map((mood) => {
          const Icon = ICONS[mood.id] || Sparkles
          const selected = active === mood.id
          return (
            <button
              key={mood.id}
              type="button"
              onClick={() => void pickMood(mood.id)}
              className={`glass-panel rounded-2xl p-5 text-left transition ${
                selected ? 'border-[#f5c518]/50 ring-1 ring-[#f5c518]/30' : 'hover:border-white/20'
              }`}
            >
              <Icon className={`mb-3 ${selected ? 'text-[#f5c518]' : 'text-white/50'}`} size={24} />
              <p className="font-semibold">{mood.label}</p>
              <p className="mt-1 text-xs text-white/40 line-clamp-2">{mood.query}</p>
            </button>
          )
        })}
      </div>

      {loading ? (
        <div className="mt-10"><MovieRailSkeleton count={4} /></div>
      ) : movies.length > 0 ? (
        <section className="mt-10">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-2xl font-bold">Picks for your mood</h2>
            <Link
              to={`/chat?q=${encodeURIComponent(moods.find((m) => m.id === active)?.query || '')}`}
              className="text-sm text-[#f5c518] hover:underline"
            >
              Refine in AI Chat →
            </Link>
          </div>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {movies.map((movie) => (
              <MovieCard
                key={movie.title}
                title={movie.title}
                poster={movie.poster}
                subtitle={movie.genre}
                rating={movie.imdb_rating ?? (movie as { total_rating?: number }).total_rating}
                explanation={movie.explanation}
                showQuickSave
                to={`/movie/${encodeURIComponent(movie.title)}`}
              />
            ))}
          </div>
        </section>
      ) : active ? (
        <p className="mt-10 text-center text-white/50">No picks found for this mood.</p>
      ) : null}
    </div>
  )
}
