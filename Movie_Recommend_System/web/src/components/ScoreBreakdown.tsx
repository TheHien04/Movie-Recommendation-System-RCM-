type Breakdown = Record<string, number>

const LABELS: Record<string, string> = {
  semantic: 'Semantic (Transformer)',
  svd: 'SVD Collaborative',
  neural: 'NeuMF Neural CF',
  rules: 'Business Rules',
  imdb: 'IMDb Quality',
}

export function ScoreBreakdown({ breakdown, score }: { breakdown: Breakdown; score?: number | null }) {
  const entries = Object.entries(breakdown).filter(([, v]) => typeof v === 'number' && v > 0)
  if (!entries.length) return null
  const max = Math.max(...entries.map(([, v]) => v), 0.001)

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-semibold">Hybrid Score Breakdown</h3>
        {score != null && (
          <span className="rounded-full bg-[#f5c518]/20 px-3 py-1 text-sm font-semibold text-[#f5c518]">
            {score.toFixed(3)}
          </span>
        )}
      </div>
      <div className="space-y-3">
        {entries.map(([key, val]) => (
          <div key={key}>
            <div className="mb-1 flex justify-between text-sm">
              <span className="text-white/70">{LABELS[key] || key}</span>
              <span className="text-white/50">{val.toFixed(3)}</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-black/40">
              <div
                className="h-full rounded-full bg-gradient-to-r from-[#f5c518] to-amber-400"
                style={{ width: `${Math.min(100, (val / max) * 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
