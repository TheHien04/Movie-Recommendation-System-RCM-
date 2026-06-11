export type Theme = 'dark' | 'light'

const KEY = 'cinemate_theme'

export function getTheme(): Theme {
  const saved = localStorage.getItem(KEY)
  return saved === 'light' ? 'light' : 'dark'
}

export function setTheme(theme: Theme) {
  localStorage.setItem(KEY, theme)
  document.documentElement.dataset.theme = theme
  window.dispatchEvent(new Event('cinemate:theme'))
}

export function initTheme() {
  document.documentElement.dataset.theme = getTheme()
}
