import { Moon, Sun, Languages } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useI18n } from '../lib/i18n'
import { getTheme, setTheme, type Theme } from '../lib/theme'

export function AppSettings() {
  const { locale, setLocale, t } = useI18n()
  const [theme, setThemeState] = useState<Theme>(getTheme)

  useEffect(() => {
    const onTheme = () => setThemeState(getTheme())
    window.addEventListener('cinemate:theme', onTheme)
    return () => window.removeEventListener('cinemate:theme', onTheme)
  }, [])

  function toggleTheme() {
    const next: Theme = theme === 'dark' ? 'light' : 'dark'
    setTheme(next)
    setThemeState(next)
  }

  function toggleLocale() {
    setLocale(locale === 'en' ? 'vi' : 'en')
  }

  return (
    <div className="flex items-center gap-1">
      <button
        type="button"
        onClick={toggleLocale}
        title="Language"
        className="inline-flex items-center gap-1 rounded-full border border-white/10 px-2.5 py-1.5 text-xs hover:bg-white/10"
      >
        <Languages size={12} />
        {locale === 'en' ? t('lang.vi') : t('lang.en')}
      </button>
      <button
        type="button"
        onClick={toggleTheme}
        title={theme === 'dark' ? t('theme.light') : t('theme.dark')}
        className="rounded-full border border-white/10 p-1.5 hover:bg-white/10"
      >
        {theme === 'dark' ? <Sun size={14} /> : <Moon size={14} />}
      </button>
    </div>
  )
}
