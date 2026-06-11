import { useEffect, useState } from 'react'
import { Bookmark, BookmarkCheck } from 'lucide-react'
import { getWatchlist, isInWatchlist, toggleWatchlist, WATCHLIST_EVENT } from '../lib/watchlist'
import { toast } from './Toast'

type Props = {
  title: string
  className?: string
}

export function SaveWatchlistButton({ title, className = '' }: Props) {
  const [saved, setSaved] = useState(() => isInWatchlist(title))

  useEffect(() => {
    setSaved(isInWatchlist(title))
    const onUpdate = () => setSaved(isInWatchlist(title))
    window.addEventListener(WATCHLIST_EVENT, onUpdate)
    return () => window.removeEventListener(WATCHLIST_EVENT, onUpdate)
  }, [title])

  async function handleClick() {
    const adding = await toggleWatchlist(title)
    setSaved(adding)
    toast(adding ? `Added "${title}" to watchlist` : `Removed "${title}" from watchlist`)
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className={`inline-flex items-center gap-2 rounded-full px-5 py-3 font-medium transition ${
        saved
          ? 'bg-emerald-500/20 border border-emerald-400/50 text-emerald-300'
          : 'border border-white/20 hover:border-[#f5c518]/50 hover:bg-white/5'
      } ${className}`}
    >
      {saved ? <BookmarkCheck size={16} /> : <Bookmark size={16} />}
      {saved ? 'Saved to Watchlist' : 'Add to Watchlist'}
    </button>
  )
}

export function useWatchlistCount() {
  const [count, setCount] = useState(getWatchlist().length)
  useEffect(() => {
    const update = () => setCount(getWatchlist().length)
    window.addEventListener(WATCHLIST_EVENT, update)
    return () => window.removeEventListener(WATCHLIST_EVENT, update)
  }, [])
  return count
}
