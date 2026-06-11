import { Star } from 'lucide-react'
import { useEffect, useState } from 'react'
import { getLocalRating, setMovieRating } from '../lib/ratings'

type Props = {
  title: string
  size?: number
  showLabel?: boolean
}

export function StarRating({ title, size = 20, showLabel = true }: Props) {
  const [value, setValue] = useState<number | null>(null)
  const [hover, setHover] = useState(0)

  useEffect(() => {
    setValue(getLocalRating(title))
    const onUpdate = () => setValue(getLocalRating(title))
    window.addEventListener('cinemate:ratings', onUpdate)
    return () => window.removeEventListener('cinemate:ratings', onUpdate)
  }, [title])

  async function rate(stars: number) {
    setValue(stars)
    await setMovieRating(title, stars)
  }

  return (
    <div className="flex items-center gap-2">
      <div className="flex" onMouseLeave={() => setHover(0)}>
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            aria-label={`Rate ${star} stars`}
            onMouseEnter={() => setHover(star)}
            onClick={() => void rate(star)}
            className="p-0.5 transition hover:scale-110"
          >
            <Star
              size={size}
              className={
                (hover || value || 0) >= star
                  ? 'fill-[#f5c518] text-[#f5c518]'
                  : 'text-white/25'
              }
            />
          </button>
        ))}
      </div>
      {showLabel && (
        <span className="text-sm text-white/50">
          {value ? `Your rating: ${value}/5` : 'Rate this movie'}
        </span>
      )}
    </div>
  )
}
