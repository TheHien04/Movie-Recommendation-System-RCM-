import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { LoaderCircle } from 'lucide-react'
import { fetchGenres } from '../lib/api'
import { MovieCard } from '../components/MovieCard'

type GenreSection = { name: string; movies: { title: string; poster?: string; overview?: string; imdb_rating?: number }[] }

export function Genres() {
  const [sections, setSections] = useState<GenreSection[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    document.title = 'Genres — Cinemate'
    fetchGenres()
      .then(setSections)
      .catch(() => setError('Could not load genres. Make sure the backend is running.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center gap-2 text-white/60">
        <LoaderCircle className="animate-spin" size={20} /> Loading genres...
      </div>
    )
  }

  if (error || sections.length === 0) {
    return (
      <div className="mx-auto max-w-xl px-4 py-20 text-center">
        <p className="text-red-300">{error || 'No genre data available.'}</p>
        <Link to="/" className="mt-4 inline-block text-[#f5c518]">Back to Home</Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-6">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Browse by Genre</h1>
        <p className="mt-2 text-white/60">Top-rated picks in each category from our catalog</p>
      </div>

      {sections.map((section) => (
        <section key={section.name} className="mb-10">
          <h2 className="mb-4 text-2xl font-semibold">{section.name}</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {section.movies.map((movie) => (
              <MovieCard
                key={`${section.name}-${movie.title}`}
                title={movie.title}
                poster={movie.poster}
                subtitle={movie.overview}
                rating={movie.imdb_rating}
                showQuickSave
                to={`/movie/${encodeURIComponent(movie.title)}`}
              />
            ))}
          </div>
        </section>
      ))}
    </div>
  )
}
