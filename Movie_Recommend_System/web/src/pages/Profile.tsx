import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { fetchProfile, login, register } from '../lib/api'
import { clearAuth, getUser, setAuth } from '../lib/auth'
import { syncRatingsFromCloud } from '../lib/ratings'
import { mergeWatchlistFromCloud } from '../lib/watchlist'
import { toast } from '../components/Toast'

export function Profile() {
  const [user, setUser] = useState(getUser())
  const [stats, setStats] = useState<{ watchlist: number; chat_messages: number; ratings?: number } | null>(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [error, setError] = useState('')

  useEffect(() => {
    document.title = 'Profile — Cinemate'
    if (user) {
      fetchProfile().then((d) => setStats(d.stats)).catch(() => setStats(null))
    }
  }, [user])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    try {
      const fn = mode === 'login' ? login : register
      const data = await fn(email, password)
      setAuth(data.token, data.user)
      setUser(data.user)
      const merged = await mergeWatchlistFromCloud()
      await syncRatingsFromCloud()
      toast(`Welcome! ${merged.length} movie${merged.length !== 1 ? 's' : ''} in watchlist`)
    } catch {
      setError('Authentication failed')
    }
  }

  function logout() {
    clearAuth()
    setUser(null)
    setStats(null)
  }

  return (
    <div className="mx-auto max-w-xl px-4 py-10 md:px-6">
      <h1 className="text-4xl font-bold">Profile</h1>
      <p className="mt-2 text-white/60">Sync watchlist and chat history across devices</p>

      {user ? (
        <div className="glass-panel mt-8 space-y-4 rounded-3xl p-6">
          <p><span className="text-white/50">Name:</span> {user.display_name}</p>
          <p><span className="text-white/50">Email:</span> {user.email}</p>
          {stats && (
            <div className="grid grid-cols-3 gap-3">
              <div className="rounded-xl bg-white/5 p-4 text-center"><p className="text-2xl font-bold">{stats.watchlist}</p><p className="text-sm text-white/50">Watchlist</p></div>
              <div className="rounded-xl bg-white/5 p-4 text-center"><p className="text-2xl font-bold">{stats.ratings ?? 0}</p><p className="text-sm text-white/50">Ratings</p></div>
              <div className="rounded-xl bg-white/5 p-4 text-center"><p className="text-2xl font-bold">{stats.chat_messages}</p><p className="text-sm text-white/50">Chat msgs</p></div>
            </div>
          )}
          <button type="button" onClick={logout} className="w-full rounded-xl border border-red-400/40 py-3 text-red-300">Sign Out</button>
        </div>
      ) : (
        <form onSubmit={onSubmit} className="glass-panel mt-8 space-y-4 rounded-3xl p-6">
          <div className="flex gap-2">
            <button type="button" onClick={() => setMode('login')} className={`flex-1 rounded-xl py-2 ${mode === 'login' ? 'bg-[#f5c518] text-black' : 'bg-white/10'}`}>Login</button>
            <button type="button" onClick={() => setMode('register')} className={`flex-1 rounded-xl py-2 ${mode === 'register' ? 'bg-[#f5c518] text-black' : 'bg-white/10'}`}>Register</button>
          </div>
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="Email" className="w-full rounded-xl border border-white/10 bg-black/30 px-4 py-3" required />
          <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Password" className="w-full rounded-xl border border-white/10 bg-black/30 px-4 py-3" required />
          {error && <p className="text-red-300 text-sm">{error}</p>}
          <button type="submit" className="w-full rounded-xl bg-[#f5c518] py-3 font-semibold text-black">{mode === 'login' ? 'Sign In' : 'Create Account'}</button>
        </form>
      )}
    </div>
  )
}
