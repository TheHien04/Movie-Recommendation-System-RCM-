import { X, Star, Play } from 'lucide-react'
import type { MovieDetails } from '../lib/api'
import { SaveWatchlistButton } from './SaveWatchlistButton'

type Props = {
  movie: MovieDetails | null
  loading?: boolean
  onClose: () => void
}

export function MovieModal({ movie, loading, onClose }: Props) {
  if (!movie && !loading) return null

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 p-4" onClick={onClose}>
      <div
        className="glass-panel max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-3xl p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex justify-end">
          <button type="button" onClick={onClose} className="rounded-full bg-white/10 p-2 hover:bg-white/20">
            <X size={18} />
          </button>
        </div>

        {loading ? (
          <div className="py-20 text-center text-white/60">Loading movie details...</div>
        ) : movie ? (
          <div className="grid gap-6 md:grid-cols-[220px_1fr]">
            <img src={movie.poster} alt={movie.title} className="w-full rounded-2xl object-cover" />
            <div className="space-y-4">
              <h2 className="text-3xl font-bold">{movie.title}</h2>
              <p className="text-white/70">{movie.overview}</p>
              <div className="grid gap-2 text-sm text-white/80 md:grid-cols-2">
                <p><span className="text-white/50">Genre:</span> {movie.genre}</p>
                <p><span className="text-white/50">Director:</span> {movie.director}</p>
                <p><span className="text-white/50">Cast:</span> {movie.actors}</p>
                <p><span className="text-white/50">Runtime:</span> {movie.runtime} min</p>
              </div>
              <div className="flex flex-wrap gap-4 text-sm">
                <span className="inline-flex items-center gap-1 text-[#f5c518]"><Star size={14} /> IMDb {movie.ratingIMDB}</span>
                <span>Rotten {movie.ratingRotten}%</span>
                <span>TMDB {movie.ratingTMDB}</span>
              </div>
              <div className="flex flex-wrap gap-3">
                <SaveWatchlistButton title={movie.title} />
                {movie.trailer && (
                  <a
                    href={movie.trailer}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 rounded-full bg-[#f5c518] px-5 py-3 font-semibold text-black"
                  >
                    <Play size={16} /> Watch Trailer
                  </a>
                )}
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  )
}
