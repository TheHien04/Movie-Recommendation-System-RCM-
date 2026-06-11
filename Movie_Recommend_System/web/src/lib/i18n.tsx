import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'

export type Locale = 'en' | 'vi'

const STORAGE_KEY = 'cinemate_locale'

const messages = {
  en: {
    'nav.home': 'Home',
    'nav.search': 'Search',
    'nav.genres': 'Genres',
    'nav.moods': 'Moods',
    'nav.compare': 'Compare',
    'nav.chat': 'AI Chat',
    'nav.watchlist': 'Watchlist',
    'nav.profile': 'Profile',
    'nav.leaderboard': 'Leaderboard',
    'nav.mlBattle': 'ML Battle',
    'nav.admin': 'Admin',
    'nav.quickSearch': 'Quick search movies...',
    'home.badge': 'Production-ready ML movie platform',
    'home.title': 'Discover movies with enterprise-grade AI',
    'home.subtitle':
      'Semantic search, hybrid recommendations, RAG chat, personalization, A/B testing, and B2B APIs — built for real-world launch.',
    'home.chat': 'Start AI Chat',
    'home.explore': 'Explore Catalog',
    'home.moods': 'Mood Discovery',
    'home.trending': 'Trending Now',
    'home.trendingSub': 'Live signals from TMDB + catalog',
    'home.forYou': 'For You',
    'home.forYouSub': 'Personalized from your watchlist & clicks',
    'home.recent': 'Continue Watching',
    'home.recentSub': 'Recently viewed on this device',
    'home.featured': 'Featured Today',
    'home.featuredSub': 'Editorial high-rated picks',
    'home.prompts': 'Quick Prompts',
    'footer.tagline': 'Built with hybrid ML under the hood (semantic search, collaborative filtering, RAG).',
    'footer.ml': 'ML Studio',
    'footer.dev': 'Developer docs',
    'theme.light': 'Light',
    'theme.dark': 'Dark',
    'lang.en': 'EN',
    'lang.vi': 'VI',
    'onboarding.title': 'Welcome to Cinemate',
    'onboarding.body':
      'Explore AI recommendations, save your watchlist, rate movies, and compare Hybrid vs RAG in ML Battle.',
    'onboarding.start': 'Get started',
    'onboarding.skip': 'Skip tour',
    'share.copied': 'Share link copied!',
    'share.watchlist': 'Share watchlist',
    'common.loading': 'Loading...',
    'common.notFound': 'Not found',
  },
  vi: {
    'nav.home': 'Trang chủ',
    'nav.search': 'Tìm kiếm',
    'nav.genres': 'Thể loại',
    'nav.moods': 'Tâm trạng',
    'nav.compare': 'So sánh',
    'nav.chat': 'AI Chat',
    'nav.watchlist': 'Danh sách',
    'nav.profile': 'Hồ sơ',
    'nav.leaderboard': 'Bảng xếp hạng',
    'nav.mlBattle': 'ML Battle',
    'nav.admin': 'Quản trị',
    'nav.quickSearch': 'Tìm phim nhanh...',
    'home.badge': 'Nền tảng gợi ý phim ML production-ready',
    'home.title': 'Khám phá phim với AI cấp doanh nghiệp',
    'home.subtitle':
      'Tìm kiếm ngữ nghĩa, gợi ý hybrid, chat RAG, cá nhân hóa, A/B testing và API B2B — sẵn sàng triển khai thực tế.',
    'home.chat': 'Bắt đầu AI Chat',
    'home.explore': 'Khám phá kho phim',
    'home.moods': 'Gợi ý theo tâm trạng',
    'home.trending': 'Đang thịnh hành',
    'home.trendingSub': 'Tín hiệu TMDB + catalog',
    'home.forYou': 'Dành cho bạn',
    'home.forYouSub': 'Cá nhân hóa từ watchlist & lượt click',
    'home.recent': 'Xem tiếp',
    'home.recentSub': 'Phim vừa xem trên thiết bị này',
    'home.featured': 'Nổi bật hôm nay',
    'home.featuredSub': 'Phim chất lượng cao được chọn lọc',
    'home.prompts': 'Gợi ý nhanh',
    'footer.tagline': 'Xây dựng với hybrid ML (semantic search, collaborative filtering, RAG).',
    'footer.ml': 'ML Studio',
    'footer.dev': 'Tài liệu dev',
    'theme.light': 'Sáng',
    'theme.dark': 'Tối',
    'lang.en': 'EN',
    'lang.vi': 'VI',
    'onboarding.title': 'Chào mừng đến Cinemate',
    'onboarding.body':
      'Khám phá gợi ý AI, lưu watchlist, chấm điểm phim và so sánh Hybrid vs RAG trong ML Battle.',
    'onboarding.start': 'Bắt đầu',
    'onboarding.skip': 'Bỏ qua',
    'share.copied': 'Đã sao chép link chia sẻ!',
    'share.watchlist': 'Chia sẻ watchlist',
    'common.loading': 'Đang tải...',
    'common.notFound': 'Không tìm thấy',
  },
} as const

export type MessageKey = keyof typeof messages.en

type I18nContextValue = {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: (key: MessageKey) => string
}

const I18nContext = createContext<I18nContextValue | null>(null)

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved === 'vi' ? 'vi' : 'en'
  })

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next)
    localStorage.setItem(STORAGE_KEY, next)
    document.documentElement.lang = next
  }, [])

  useEffect(() => {
    document.documentElement.lang = locale
  }, [locale])

  const t = useCallback(
    (key: MessageKey) => messages[locale][key] ?? messages.en[key] ?? key,
    [locale],
  )

  const value = useMemo(() => ({ locale, setLocale, t }), [locale, setLocale, t])

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export function useI18n() {
  const ctx = useContext(I18nContext)
  if (!ctx) throw new Error('useI18n must be used within I18nProvider')
  return ctx
}
