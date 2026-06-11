import { useEffect, useState } from 'react'
import { Code2, KeyRound } from 'lucide-react'
import { fetchApiDocs, fetchFeedbackStats } from '../lib/api'

export function Developers() {
  const [docs, setDocs] = useState<Record<string, unknown> | null>(null)
  const [stats, setStats] = useState<Record<string, unknown> | null>(null)

  useEffect(() => {
    document.title = 'Developers — Cinemate B2B API'
    fetchApiDocs().then(setDocs).catch(() => setDocs(null))
    fetchFeedbackStats().then(setStats).catch(() => setStats(null))
  }, [])

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 md:px-6">
      <div className="flex items-center gap-3">
        <Code2 className="text-[#f5c518]" size={32} />
        <div>
          <h1 className="text-4xl font-bold">Developer API</h1>
          <p className="text-white/60">For partners &amp; engineers only — not needed for normal users</p>
          <p className="mt-2 text-sm text-white/40">The website already uses this API behind the scenes. This page is documentation if you want to embed Cinemate in another app.</p>
        </div>
      </div>

      <section className="glass-panel mt-8 rounded-3xl p-6">
        <h2 className="flex items-center gap-2 text-xl font-semibold"><KeyRound size={18} /> Authentication</h2>
        <p className="mt-2 text-white/70">Send header <code className="text-[#f5c518]">X-API-Key: your_key</code> to B2B endpoints.</p>
        <p className="mt-2 text-sm text-white/50">Create keys via POST /api/admin/keys (admin use).</p>
      </section>

      <section className="glass-panel mt-6 rounded-3xl p-6">
        <h2 className="text-xl font-semibold">API Reference</h2>
        <pre className="mt-4 overflow-x-auto rounded-2xl bg-black/40 p-4 text-sm text-emerald-300">{JSON.stringify(docs, null, 2)}</pre>
      </section>

      <section className="glass-panel mt-6 rounded-3xl p-6">
        <h2 className="text-xl font-semibold">A/B Feedback Analytics</h2>
        <pre className="mt-4 overflow-x-auto rounded-2xl bg-black/40 p-4 text-sm">{JSON.stringify(stats, null, 2)}</pre>
      </section>

      <section className="mt-8 rounded-3xl border border-[#f5c518]/30 bg-[#f5c518]/10 p-6">
        <h2 className="text-xl font-bold">Monetization Ready</h2>
        <p className="mt-2 text-white/70">Freemium tiers, affiliate watch links, and B2B API billing can be enabled on this stack. Contact for enterprise SLA.</p>
      </section>
    </div>
  )
}
