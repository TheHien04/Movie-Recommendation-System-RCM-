import { useState } from 'react'
import type { FormEvent } from 'react'
import { Swords } from 'lucide-react'
import { fetchRecommendations } from '../lib/api'
import type { Recommendation } from '../lib/api'
import { MovieCard } from '../components/MovieCard'

export function MLBattle() {
  const [query, setQuery] = useState('mind-bending sci-fi movies like Inception')
  const [hybrid, setHybrid] = useState<Recommendation[]>([])
  const [rag, setRag] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(false)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    try {
      const [h, r] = await Promise.all([
        fetchRecommendations(query, 'hybrid'),
        fetchRecommendations(query, 'rag'),
      ])
      setHybrid(h.recommended_movies)
      setRag(r.recommended_movies)
    } catch {
      setHybrid([])
      setRag([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-6">
      <div className="flex items-center gap-3">
        <Swords className="text-[#f5c518]" size={32} />
        <div>
          <h1 className="text-4xl font-bold">ML Battle</h1>
          <p className="mt-1 text-white/60">Side-by-side: Hybrid v3 vs RAG for the same query</p>
        </div>
      </div>

      <form onSubmit={onSubmit} className="glass-panel mt-8 flex gap-3 rounded-2xl p-4">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter a recommendation query..."
          className="flex-1 bg-transparent py-3 outline-none"
        />
        <button type="submit" disabled={loading} className="rounded-xl bg-[#f5c518] px-6 font-semibold text-black disabled:opacity-50">
          {loading ? 'Battling...' : 'Compare'}
        </button>
      </form>

      {(hybrid.length > 0 || rag.length > 0) && (
        <div className="mt-10 grid gap-8 lg:grid-cols-2">
          <BattleColumn title="Hybrid v3" subtitle="Transformer + SVD + NeuMF + MMR" movies={hybrid} accent="emerald" />
          <BattleColumn title="RAG" subtitle="LLM retrieval-augmented generation" movies={rag} accent="violet" />
        </div>
      )}
    </div>
  )
}

function BattleColumn({
  title,
  subtitle,
  movies,
  accent,
}: {
  title: string
  subtitle: string
  movies: Recommendation[]
  accent: 'emerald' | 'violet'
}) {
  const border = accent === 'emerald' ? 'border-emerald-500/30' : 'border-violet-500/30'
  return (
    <section className={`glass-panel rounded-3xl border ${border} p-6`}>
      <h2 className="text-xl font-bold">{title}</h2>
      <p className="text-sm text-white/50">{subtitle}</p>
      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        {movies.slice(0, 6).map((m) => (
          <MovieCard
            key={m.title}
            title={m.title}
            poster={m.poster}
            rating={m.total_rating}
            subtitle={m.explanation}
            showQuickSave
            to={`/movie/${encodeURIComponent(m.title)}`}
          />
        ))}
      </div>
    </section>
  )
}
