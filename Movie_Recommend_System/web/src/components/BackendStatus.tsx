import { useEffect, useState } from 'react'
import { getApiBase } from '../lib/config'

async function checkHealth(): Promise<boolean> {
  const base = getApiBase()

  const url = `${base}/api/health/live`
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 90_000)
  try {
    const res = await fetch(url, { signal: controller.signal })
    return res.ok
  } finally {
    clearTimeout(timer)
  }
}

export function BackendStatus() {
  const [online, setOnline] = useState<boolean | null>(null)
  const [waking, setWaking] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function poll() {
      setWaking(true)
      const ok = await checkHealth().catch(() => false)
      if (!cancelled) {
        setOnline(ok)
        setWaking(false)
      }
    }
    void poll()
    const timer = setInterval(() => void poll(), 30_000)
    return () => {
      cancelled = true
      clearInterval(timer)
    }
  }, [])

  if (online === null && waking) {
    return (
      <span className="hidden items-center gap-2 rounded-full bg-amber-500/15 px-3 py-1 text-xs text-amber-200 md:inline-flex">
        <span className="h-2 w-2 animate-pulse rounded-full bg-amber-400" />
        Waking API…
      </span>
    )
  }

  if (online === null) return null

  return (
    <span
      className={`hidden items-center gap-2 rounded-full px-3 py-1 text-xs md:inline-flex ${
        online ? 'bg-emerald-500/15 text-emerald-300' : 'bg-red-500/15 text-red-300'
      }`}
    >
      <span className={`h-2 w-2 rounded-full ${online ? 'bg-emerald-400' : 'bg-red-400'}`} />
      API {online ? 'Online' : 'Offline'}
    </span>
  )
}
