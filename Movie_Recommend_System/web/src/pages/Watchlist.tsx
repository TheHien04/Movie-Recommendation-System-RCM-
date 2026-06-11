import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { fetchMovieDetails, fetchMoviesBatch } from '../lib/api'
import type { MovieDetails } from '../lib/api'
import { MovieCard } from '../components/MovieCard'
import { MovieModal } from '../components/MovieModal'
import { MovieRailSkeleton } from '../components/LoadingSkeleton'
import { Download, Share2 } from 'lucide-react'
import {
  decodeWatchlistShare,
  encodeWatchlistShare,
  getWatchlist,
  mergeWatchlistTitles,
  toggleWatchlist,
  WATCHLIST_EVENT,
} from '../lib/watchlist'
import { toast } from '../components/Toast'
import { useI18n } from '../lib/i18n'

type WatchlistItem = { title: string; poster?: string; rating?: number }

export function Watchlist() {
  const { t } = useI18n()
  const [params] = useSearchParams()
  const [items, setItems] = useState<WatchlistItem[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<MovieDetails | null>(null)
  const [loadingModal, setLoadingModal] = useState(false)

  async function loadItems() {
    const titles = getWatchlist()
    if (!titles.length) {
      setItems([])
      setLoading(false)
      return
    }
    setLoading(true)
    try {
      const batch = await fetchMoviesBatch(titles)
      const byTitle = new Map(batch.map((m) => [m.title, m]))
      setItems(
        titles.map((title) => {
          const m = byTitle.get(title)
          return { title, poster: m?.poster, rating: m?.imdb_rating }
        }),
      )
    } catch {
      setItems(titles.map((title) => ({ title })))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    document.title = 'Watchlist — Cinemate'
    const share = params.get('share')
    if (share) {
      const titles = decodeWatchlistShare(share)
      if (titles.length) {
        void mergeWatchlistTitles(titles).then((added) => {
          if (added > 0) toast(`Imported ${added} movie${added !== 1 ? 's' : ''} from share link`)
          void loadItems()
        })
        return
      }
    }
    void loadItems()
    const onUpdate = () => void loadItems()
    window.addEventListener(WATCHLIST_EVENT, onUpdate)
    return () => window.removeEventListener(WATCHLIST_EVENT, onUpdate)
  }, [params])

  async function openMovie(title: string) {
    setLoadingModal(true)
    try {
      setSelected(await fetchMovieDetails(title))
    } finally {
      setLoadingModal(false)
    }
  }

  async function remove(title: string) {
    await toggleWatchlist(title)
    toast(`Removed "${title}" from watchlist`)
    void loadItems()
  }

  function exportWatchlist(format: 'json' | 'csv') {
    const titles = getWatchlist()
    if (!titles.length) return
    const blob =
      format === 'json'
        ? new Blob([JSON.stringify({ watchlist: titles, exported_at: new Date().toISOString() }, null, 2)], {
            type: 'application/json',
          })
        : new Blob([`title\n${titles.map((t) => `"${t.replace(/"/g, '""')}"`).join('\n')}`], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `cinemate-watchlist.${format}`
    a.click()
    URL.revokeObjectURL(url)
    toast(`Exported ${titles.length} movies as ${format.toUpperCase()}`)
  }

  async function shareWatchlist() {
    const titles = getWatchlist()
    if (!titles.length) return
    const url = `${window.location.origin}/watchlist?share=${encodeURIComponent(encodeWatchlistShare(titles))}`
    try {
      await navigator.clipboard.writeText(url)
      toast(t('share.copied'))
    } catch {
      toast(url)
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold">My Watchlist</h1>
          <p className="mt-2 text-white/60">{items.length} movie{items.length !== 1 ? 's' : ''} saved</p>
        </div>
        {items.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => void shareWatchlist()} className="inline-flex items-center gap-2 rounded-xl border border-[#f5c518]/40 px-4 py-2 text-sm text-[#f5c518] hover:bg-[#f5c518]/10">
              <Share2 size={14} /> {t('share.watchlist')}
            </button>
            <button type="button" onClick={() => exportWatchlist('json')} className="inline-flex items-center gap-2 rounded-xl border border-white/15 px-4 py-2 text-sm hover:bg-white/5">
              <Download size={14} /> JSON
            </button>
            <button type="button" onClick={() => exportWatchlist('csv')} className="inline-flex items-center gap-2 rounded-xl border border-white/15 px-4 py-2 text-sm hover:bg-white/5">
              <Download size={14} /> CSV
            </button>
          </div>
        )}
      </div>

      {loading ? (
        <div className="mt-8"><MovieRailSkeleton count={4} /></div>
      ) : items.length === 0 ? (
        <div className="glass-panel mt-8 rounded-3xl p-10 text-center">
          <p className="text-lg text-white/80">Your watchlist is empty</p>
          <p className="mt-2 text-white/50">Tap the bookmark icon on any movie card or open a movie detail page</p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <Link to="/" className="rounded-full bg-[#f5c518] px-6 py-3 font-semibold text-black">Browse Home</Link>
            <Link to="/chat" className="rounded-full border border-white/20 px-6 py-3 hover:bg-white/10">Get AI Picks</Link>
          </div>
        </div>
      ) : (
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {items.map((item) => (
            <div key={item.title} className="space-y-2">
              <MovieCard
                title={item.title}
                poster={item.poster}
                rating={item.rating}
                showQuickSave
                onClick={() => openMovie(item.title)}
              />
              <div className="flex gap-2">
                <Link
                  to={`/movie/${encodeURIComponent(item.title)}`}
                  className="flex-1 rounded-xl border border-white/15 py-2 text-center text-sm hover:bg-white/5"
                >
                  Details
                </Link>
                <button
                  type="button"
                  onClick={() => remove(item.title)}
                  className="flex-1 rounded-xl border border-red-400/30 py-2 text-sm text-red-300 hover:bg-red-500/10"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <MovieModal movie={selected} loading={loadingModal} onClose={() => setSelected(null)} />
    </div>
  )
}
