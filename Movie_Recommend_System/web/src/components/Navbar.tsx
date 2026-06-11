import { NavLink, useNavigate } from 'react-router-dom'
import {
  Clapperboard, MessageSquare, Home, Layers, Bookmark, Search, User, Heart, GitCompare, Trophy, Swords,
} from 'lucide-react'
import { BackendStatus } from './BackendStatus'
import { AppSettings } from './AppSettings'
import { useWatchlistCount } from './SaveWatchlistButton'
import { useI18n, type MessageKey } from '../lib/i18n'
import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'

const linkDefs: { to: string; key: MessageKey; icon: typeof Home }[] = [
  { to: '/', key: 'nav.home', icon: Home },
  { to: '/search', key: 'nav.search', icon: Search },
  { to: '/genres', key: 'nav.genres', icon: Layers },
  { to: '/moods', key: 'nav.moods', icon: Heart },
  { to: '/leaderboard', key: 'nav.leaderboard', icon: Trophy },
  { to: '/ml-battle', key: 'nav.mlBattle', icon: Swords },
  { to: '/compare', key: 'nav.compare', icon: GitCompare },
  { to: '/chat', key: 'nav.chat', icon: MessageSquare },
  { to: '/watchlist', key: 'nav.watchlist', icon: Bookmark },
  { to: '/profile', key: 'nav.profile', icon: User },
]

export function Navbar() {
  const navigate = useNavigate()
  const { t } = useI18n()
  const [quick, setQuick] = useState('')
  const watchlistCount = useWatchlistCount()
  const searchRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === '/' && document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
        e.preventDefault()
        searchRef.current?.focus()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  function onQuickSearch(e: FormEvent) {
    e.preventDefault()
    if (quick.trim()) navigate(`/search?q=${encodeURIComponent(quick.trim())}`)
  }

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-black/60 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-3 md:px-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-[#f5c518]/15 p-2 text-[#f5c518]"><Clapperboard size={22} /></div>
          <div>
            <p className="text-lg font-bold tracking-wide">Cinemate</p>
            <p className="text-xs text-white/50">Hybrid ML Movie Discovery</p>
          </div>
        </div>

        <form onSubmit={onQuickSearch} className="hidden flex-1 max-w-md lg:block">
          <input
            ref={searchRef}
            value={quick}
            onChange={(e) => setQuick(e.target.value)}
            placeholder={t('nav.quickSearch')}
            className="w-full rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm outline-none focus:border-[#f5c518]/50"
          />
        </form>

        <div className="flex flex-wrap items-center gap-2">
          <AppSettings />
          <BackendStatus />
          <nav className="flex flex-wrap items-center gap-1">
            {linkDefs.map(({ to, key, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `relative inline-flex items-center gap-1.5 rounded-full px-3 py-2 text-xs md:text-sm transition ${
                    isActive ? 'bg-[#f5c518] text-black font-semibold' : 'text-white/70 hover:bg-white/10'
                  }`
                }
              >
                <Icon size={14} />
                <span className="hidden sm:inline">{t(key)}</span>
                {to === '/watchlist' && watchlistCount > 0 && (
                  <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-emerald-500 px-1 text-[10px] font-bold text-white">
                    {watchlistCount}
                  </span>
                )}
              </NavLink>
            ))}
          </nav>
        </div>
      </div>
    </header>
  )
}
