import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Bot, Clock, Heart, Sparkles, TrendingUp, UserCircle } from 'lucide-react'
import { fetchMoviesBatch, fetchRandomMovies, fetchTrending, fetchPersonalized, trackEvent } from '../lib/api'
import type { MovieSummary } from '../lib/api'
import { MovieCard } from '../components/MovieCard'
import { MovieRailSkeleton } from '../components/LoadingSkeleton'
import { getRecentViews } from '../lib/history'
import { useI18n } from '../lib/i18n'
import { fetchPublicStats } from '../lib/api'

const prompts = [
  'Recommend horror movies',
  'Movies starring Leonardo DiCaprio',
  'Christopher Nolan sci-fi films',
  'Best animated family movies',
]

export function Home() {
  const { t } = useI18n()
  const [featured, setFeatured] = useState<MovieSummary[]>([])
  const [stats, setStats] = useState<{ movie_count?: number; genre_count?: number }>({})
  const [trending, setTrending] = useState<MovieSummary[]>([])
  const [personalized, setPersonalized] = useState<MovieSummary[]>([])
  const [recent, setRecent] = useState<MovieSummary[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    document.title = 'Cinemate — AI Movie Discovery Platform'
    const recentTitles = getRecentViews().slice(0, 8)
    Promise.all([
      fetchRandomMovies().catch(() => [] as MovieSummary[]),
      fetchTrending().catch(() => [] as MovieSummary[]),
      fetchPersonalized().catch(() => [] as MovieSummary[]),
      recentTitles.length ? fetchMoviesBatch(recentTitles).catch(() => [] as MovieSummary[]) : Promise.resolve([]),
      fetchPublicStats().catch(() => ({})),
    ]).then(([f, tr, p, r, st]) => {
      setFeatured(f)
      setTrending(tr)
      setPersonalized(p)
      setRecent(r)
      setStats(st as { movie_count?: number; genre_count?: number })
    }).finally(() => setLoading(false))

    const onHistory = () => {
      const titles = getRecentViews().slice(0, 8)
      if (titles.length) fetchMoviesBatch(titles).then(setRecent).catch(() => setRecent([]))
    }
    window.addEventListener('cinemate:history', onHistory)
    return () => window.removeEventListener('cinemate:history', onHistory)
  }, [])

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-6">
      <section className="glass-panel overflow-hidden rounded-[2rem] p-8 md:p-12">
        <div className="grid items-center gap-10 lg:grid-cols-2">
          <div className="space-y-6">
            <p className="inline-flex rounded-full bg-[#f5c518]/15 px-4 py-1 text-sm text-[#f5c518]">
              {t('home.badge')}
              {stats.movie_count ? ` · ${stats.movie_count} movies` : ''}
            </p>
            <h1 className="text-4xl font-black leading-tight md:text-6xl text-gradient">
              {t('home.title')}
            </h1>
            <p className="max-w-xl text-lg text-white/70">
              {t('home.subtitle')}
            </p>
            <div className="flex flex-wrap gap-3">
              <Link to="/chat" className="inline-flex items-center gap-2 rounded-full bg-[#f5c518] px-6 py-3 font-semibold text-black">
                <Bot size={18} /> {t('home.chat')}
              </Link>
              <Link to="/search" className="inline-flex items-center gap-2 rounded-full border border-white/15 px-6 py-3 hover:bg-white/10">
                <Sparkles size={18} /> {t('home.explore')}
              </Link>
              <Link to="/moods" className="inline-flex items-center gap-2 rounded-full border border-[#f5c518]/30 px-6 py-3 text-[#f5c518] hover:bg-[#f5c518]/10">
                <Heart size={18} /> {t('home.moods')}
              </Link>
              <Link to="/ml-battle" className="inline-flex items-center gap-2 rounded-full border border-white/15 px-6 py-3 hover:bg-white/10">
                ML Battle
              </Link>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {['Semantic RAG', 'SVD-CF Hybrid', 'MMR Diversity', 'NDCG + A/B'].map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-white/5 p-5">
                <p className="text-sm text-white/50">Stack</p>
                <p className="mt-2 font-semibold">{item}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {loading ? (
        <div className="mt-12 space-y-12">
          <MovieRailSkeleton />
          <MovieRailSkeleton />
        </div>
      ) : (
        <>
          {recent.length > 0 && (
            <MovieRail icon={Clock} title={t('home.recent')} subtitle={t('home.recentSub')} movies={recent} />
          )}
          <MovieRail icon={TrendingUp} title={t('home.trending')} subtitle={t('home.trendingSub')} movies={trending} />
          <MovieRail icon={UserCircle} title={t('home.forYou')} subtitle={t('home.forYouSub')} movies={personalized} />
          <MovieRail title={t('home.featured')} subtitle={t('home.featuredSub')} movies={featured} />
        </>
      )}

      <section className="mt-12">
        <h2 className="mb-4 text-2xl font-bold">{t('home.prompts')}</h2>
        <div className="grid gap-3 md:grid-cols-2">
          {prompts.map((prompt) => (
            <Link key={prompt} to={`/chat?q=${encodeURIComponent(prompt)}`} className="glass-panel flex items-center justify-between rounded-2xl px-5 py-4 hover:border-[#f5c518]/30">
              <span>{prompt}</span>
              <ArrowRight size={18} className="text-[#f5c518]" />
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}

function MovieRail({ title, subtitle, movies, icon: Icon }: { title: string; subtitle: string; movies: MovieSummary[]; icon?: typeof TrendingUp }) {
  if (!movies.length) return null
  return (
    <section className="mt-12">
      <div className="mb-4 flex items-center gap-2">
        {Icon && <Icon className="text-[#f5c518]" size={20} />}
        <div>
          <h2 className="text-2xl font-bold">{title}</h2>
          <p className="text-white/60">{subtitle}</p>
        </div>
      </div>
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {movies.map((movie) => (
          <MovieCard
            key={movie.title}
            title={movie.title}
            poster={movie.poster}
            subtitle={movie.description || movie.genre}
            rating={movie.imdb_rating}
            explanation={movie.explanation}
            showQuickSave
            to={`/movie/${encodeURIComponent(movie.title)}`}
            onClick={() => trackEvent('click', movie.title)}
          />
        ))}
      </div>
    </section>
  )
}
