import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Shield } from 'lucide-react'
import { fetchAdminDashboard } from '../lib/api'

const KEY = 'cinemate_admin_key'

type Dashboard = {
  users: number
  watchlist_items: number
  ratings: number
  feedback_total: number
  feedback_by_variant: { variant: string; avg_rating: number; count: number }[]
  events_by_type: { event_type: string; count: number }[]
  model: string
}

export function Admin() {
  const [key, setKey] = useState(() => sessionStorage.getItem(KEY) || '')
  const [input, setInput] = useState('')
  const [data, setData] = useState<Dashboard | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (key) void load(key)
  }, [key])

  async function load(adminKey: string) {
    setError('')
    try {
      setData(await fetchAdminDashboard(adminKey))
    } catch {
      setData(null)
      setError('Invalid admin key or server error')
      sessionStorage.removeItem(KEY)
      setKey('')
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    sessionStorage.setItem(KEY, input.trim())
    setKey(input.trim())
  }

  if (!key) {
    return (
      <div className="mx-auto max-w-md px-4 py-20">
        <div className="glass-panel rounded-3xl p-8 text-center">
          <Shield className="mx-auto mb-4 text-[#f5c518]" size={40} />
          <h1 className="text-2xl font-bold">Admin Dashboard</h1>
          <p className="mt-2 text-sm text-white/50">Enter ADMIN_API_KEY from server environment</p>
          <form onSubmit={onSubmit} className="mt-6 space-y-3">
            <input
              type="password"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="X-Admin-Key"
              className="w-full rounded-xl border border-white/10 bg-black/40 px-4 py-3"
            />
            <button type="submit" className="w-full rounded-xl bg-[#f5c518] py-3 font-semibold text-black">
              Unlock
            </button>
          </form>
          {error && <p className="mt-3 text-sm text-red-300">{error}</p>}
        </div>
      </div>
    )
  }

  if (!data) return <p className="p-20 text-center text-white/50">Loading dashboard...</p>

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 md:px-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <button
          type="button"
          onClick={() => { sessionStorage.removeItem(KEY); setKey(''); setData(null) }}
          className="text-sm text-white/50 hover:text-white"
        >
          Sign out
        </button>
      </div>
      <p className="mt-1 text-white/50">Model: {data.model}</p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Users', value: data.users },
          { label: 'Watchlist items', value: data.watchlist_items },
          { label: 'Ratings', value: data.ratings },
          { label: 'Feedback', value: data.feedback_total },
        ].map((s) => (
          <div key={s.label} className="glass-panel rounded-2xl p-5 text-center">
            <p className="text-3xl font-bold text-[#f5c518]">{s.value}</p>
            <p className="text-sm text-white/50">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <section className="glass-panel rounded-2xl p-6">
          <h2 className="font-semibold">A/B Feedback</h2>
          <div className="mt-4 space-y-3">
            {data.feedback_by_variant.map((r) => (
              <div key={r.variant} className="flex justify-between text-sm">
                <span>Variant {r.variant}</span>
                <span className="text-white/50">{r.count} votes · avg {r.avg_rating.toFixed(2)}</span>
              </div>
            ))}
            {!data.feedback_by_variant.length && <p className="text-white/40">No feedback yet</p>}
          </div>
        </section>
        <section className="glass-panel rounded-2xl p-6">
          <h2 className="font-semibold">Events</h2>
          <div className="mt-4 space-y-3">
            {data.events_by_type.map((r) => (
              <div key={r.event_type} className="flex justify-between text-sm">
                <span>{r.event_type}</span>
                <span className="text-white/50">{r.count}</span>
              </div>
            ))}
            {!data.events_by_type.length && <p className="text-white/40">No events yet</p>}
          </div>
        </section>
      </div>
    </div>
  )
}
