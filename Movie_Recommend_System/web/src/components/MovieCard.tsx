import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Bookmark, BookmarkCheck, Star } from 'lucide-react'
import { isInWatchlist, toggleWatchlist, WATCHLIST_EVENT } from '../lib/watchlist'
import { toast } from './Toast'

type Props = {
  title: string
  poster?: string
  subtitle?: string
  rating?: number
  explanation?: string
  onClick?: () => void
  to?: string
  showQuickSave?: boolean
}

export function MovieCard({ title, poster, subtitle, rating, explanation, onClick, to, showQuickSave }: Props) {
  const [imageError, setImageError] = useState(false)
  const [saved, setSaved] = useState(() => isInWatchlist(title))

  useEffect(() => {
    setSaved(isInWatchlist(title))
    const onUpdate = () => setSaved(isInWatchlist(title))
    window.addEventListener(WATCHLIST_EVENT, onUpdate)
    return () => window.removeEventListener(WATCHLIST_EVENT, onUpdate)
  }, [title])

  useEffect(() => {
    setImageError(false)
  }, [poster, title])

  const showPoster = Boolean(poster) && !imageError

  async function onQuickSave(e: React.MouseEvent) {
    e.preventDefault()
    e.stopPropagation()
    const adding = await toggleWatchlist(title)
    setSaved(adding)
    toast(adding ? `Saved "${title}"` : `Removed "${title}"`)
  }

  const content = (
  <>
      <div className="relative aspect-[2/3] overflow-hidden bg-gradient-to-br from-white/10 to-white/5">
        {showPoster ? (
          <img
            src={poster}
            alt={title}
            loading="lazy"
            onError={() => setImageError(true)}
            className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full flex-col items-center justify-center gap-3 p-6 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#f5c518]/15 text-2xl font-bold text-[#f5c518]">
              {title.charAt(0).toUpperCase()}
            </div>
            <p className="line-clamp-3 text-sm text-white/50">{title}</p>
          </div>
        )}
        {showQuickSave && (
          <button
            type="button"
            onClick={onQuickSave}
            aria-label={saved ? 'Remove from watchlist' : 'Add to watchlist'}
            className={`absolute right-2 top-2 rounded-full p-2 backdrop-blur-md transition ${
              saved ? 'bg-emerald-500/90 text-white' : 'bg-black/50 text-white hover:bg-[#f5c518] hover:text-black'
            }`}
          >
            {saved ? <BookmarkCheck size={16} /> : <Bookmark size={16} />}
          </button>
        )}
      </div>
      <div className="space-y-2 p-4">
        <h3 className="line-clamp-2 font-semibold">{title}</h3>
        {subtitle && <p className="line-clamp-2 text-sm text-white/60">{subtitle}</p>}
        {typeof rating === 'number' && rating > 0 && (
          <p className="inline-flex items-center gap-1 text-sm text-[#f5c518]">
            <Star size={14} fill="currentColor" />
            IMDb {rating.toFixed(1)}
          </p>
        )}
        {explanation && <p className="line-clamp-3 text-xs text-white/45">{explanation}</p>}
      </div>
  </>
  )

  const className = 'group glass-panel w-full overflow-hidden rounded-2xl text-left transition hover:-translate-y-1 hover:border-[#f5c518]/40 block'

  if (to) {
    return (
      <Link to={to} className={className} onClick={onClick}>
        {content}
      </Link>
    )
  }

  return (
    <button type="button" onClick={onClick} className={className}>
      {content}
    </button>
  )
}
