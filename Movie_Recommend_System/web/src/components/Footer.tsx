import { Link } from 'react-router-dom'
import { useI18n } from '../lib/i18n'

export function Footer() {
  const { t } = useI18n()
  return (
    <footer className="mt-16 border-t border-white/10 py-8 text-center text-sm text-white/40">
      <p>© {new Date().getFullYear()} Cinemate — AI Movie Discovery</p>
      <p className="mt-2">{t('footer.tagline')}</p>
      <div className="mt-3 flex flex-wrap justify-center gap-4">
        <Link to="/ml" className="hover:text-[#f5c518]">{t('footer.ml')}</Link>
        <Link to="/developers" className="hover:text-[#f5c518]">{t('footer.dev')}</Link>
        <Link to="/admin" className="hover:text-[#f5c518]">{t('nav.admin')}</Link>
      </div>
    </footer>
  )
}
