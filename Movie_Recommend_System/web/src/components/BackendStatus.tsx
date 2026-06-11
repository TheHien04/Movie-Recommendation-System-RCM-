import { useEffect, useState } from 'react'
import { fetchHealth } from '../lib/api'

export function BackendStatus() {
  const [online, setOnline] = useState<boolean | null>(null)

  useEffect(() => {
    const check = () => {
      fetchHealth()
        .then(() => setOnline(true))
        .catch(() => setOnline(false))
    }
    check()
    const timer = setInterval(check, 15000)
    return () => clearInterval(timer)
  }, [])

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
