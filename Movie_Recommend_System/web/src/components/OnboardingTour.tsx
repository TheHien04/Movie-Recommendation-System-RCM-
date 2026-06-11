import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Sparkles, X } from 'lucide-react'
import { useI18n } from '../lib/i18n'

const KEY = 'cinemate_onboarding_done'

export function OnboardingTour() {
  const { t } = useI18n()
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (!localStorage.getItem(KEY)) setOpen(true)
  }, [])

  function dismiss(start = false) {
    localStorage.setItem(KEY, '1')
    setOpen(false)
    if (start) window.location.href = '/chat'
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
      <div className="glass-panel relative max-w-md rounded-3xl p-8">
        <button
          type="button"
          onClick={() => dismiss(false)}
          className="absolute right-4 top-4 rounded-full p-1 hover:bg-white/10"
          aria-label="Close"
        >
          <X size={18} />
        </button>
        <div className="mb-4 inline-flex rounded-full bg-[#f5c518]/15 p-3 text-[#f5c518]">
          <Sparkles size={24} />
        </div>
        <h2 className="text-2xl font-bold">{t('onboarding.title')}</h2>
        <p className="mt-3 text-white/70">{t('onboarding.body')}</p>
        <div className="mt-6 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => dismiss(true)}
            className="rounded-full bg-[#f5c518] px-5 py-2.5 font-semibold text-black"
          >
            {t('onboarding.start')}
          </button>
          <Link
            to="/moods"
            onClick={() => dismiss(false)}
            className="rounded-full border border-white/20 px-5 py-2.5 hover:bg-white/5"
          >
            {t('home.moods')}
          </Link>
          <button type="button" onClick={() => dismiss(false)} className="text-sm text-white/50 hover:text-white/80">
            {t('onboarding.skip')}
          </button>
        </div>
      </div>
    </div>
  )
}
