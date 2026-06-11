import { useEffect, useState } from 'react'
import { BrainCircuit, Gauge, Layers3, Network } from 'lucide-react'
import { fetchFeedbackStats, fetchHealth, fetchMlInfo } from '../lib/api'

export function MLStudio() {
  const [mlInfo, setMlInfo] = useState<Record<string, unknown> | null>(null)
  const [health, setHealth] = useState<Record<string, unknown> | null>(null)
  const [feedback, setFeedback] = useState<{ variant: string; avg_rating: number; count: number }[]>([])

  useEffect(() => {
    fetchMlInfo().then(setMlInfo).catch(() => setMlInfo(null))
    fetchHealth().then(setHealth).catch(() => setHealth(null))
    fetchFeedbackStats()
      .then((d) => setFeedback((d.variants as { variant: string; avg_rating: number; count: number }[]) || []))
      .catch(() => setFeedback([]))
  }, [])

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-6">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">ML Studio</h1>
        <p className="mt-2 max-w-3xl text-white/60">
          Production-style recommender stack used in modern ML products: semantic retrieval,
          collaborative factorization, business rules, diversity re-ranking, and ranking metrics.
        </p>
      </div>

      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {[
          { icon: BrainCircuit, title: 'Transformer CBF', desc: 'Sentence-BERT (MiniLM) + TF-IDF fallback' },
          { icon: Network, title: 'NeuMF Neural CF', desc: 'PyTorch GMF+MLP collaborative filtering' },
          { icon: Layers3, title: 'Hybrid v3 Fusion', desc: 'SVD + neural + semantic, grid-search tuned' },
          { icon: Gauge, title: 'MMR + NDCG Gate', desc: 'Diversity reranking + offline eval in CI' },
        ].map(({ icon: Icon, title, desc }) => (
          <div key={title} className="glass-panel rounded-2xl p-5">
            <Icon className="mb-3 text-[#f5c518]" />
            <h3 className="font-semibold">{title}</h3>
            <p className="mt-2 text-sm text-white/60">{desc}</p>
          </div>
        ))}
      </div>

      {feedback.length > 0 && (
        <section className="glass-panel mt-8 rounded-3xl p-6">
          <h2 className="text-xl font-semibold">A/B Feedback (live)</h2>
          <p className="mt-1 text-sm text-white/50">Thumbs up/down from users on Hybrid vs RAG recommendations</p>
          <div className="mt-6 space-y-4">
            {feedback.map((row) => (
              <div key={row.variant}>
                <div className="mb-1 flex justify-between text-sm">
                  <span>Variant {row.variant}</span>
                  <span className="text-white/50">{row.count} votes · avg {row.avg_rating.toFixed(2)}</span>
                </div>
                <div className="h-3 overflow-hidden rounded-full bg-black/40">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-[#f5c518]"
                    style={{ width: `${Math.min(100, ((row.avg_rating + 1) / 2) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      <div className="mt-8 grid gap-5 lg:grid-cols-2">
        <section className="glass-panel rounded-3xl p-6">
          <h2 className="text-xl font-semibold">Live Pipeline Config</h2>
          <pre className="mt-4 overflow-x-auto rounded-2xl bg-black/40 p-4 text-sm text-[#f5c518]">
            {JSON.stringify(mlInfo, null, 2)}
          </pre>
        </section>
        <section className="glass-panel rounded-3xl p-6">
          <h2 className="text-xl font-semibold">Service Health</h2>
          <pre className="mt-4 overflow-x-auto rounded-2xl bg-black/40 p-4 text-sm text-emerald-300">
            {JSON.stringify(health, null, 2)}
          </pre>
          <p className="mt-4 text-sm text-white/60">
            Run offline evaluation: <code className="text-[#f5c518]">python evaluation_movies.py</code>
          </p>
        </section>
      </div>
    </div>
  )
}
