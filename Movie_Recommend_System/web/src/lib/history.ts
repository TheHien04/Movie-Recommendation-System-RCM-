const KEY = 'cinemate_recent_views'
const MAX = 12

export function addRecentView(title: string) {
  if (!title.trim()) return
  const list = getRecentViews().filter((t) => t !== title)
  list.unshift(title)
  localStorage.setItem(KEY, JSON.stringify(list.slice(0, MAX)))
  window.dispatchEvent(new Event('cinemate:history'))
}

export function getRecentViews(): string[] {
  try {
    const raw = localStorage.getItem(KEY)
    return raw ? (JSON.parse(raw) as string[]) : []
  } catch {
    return []
  }
}

export function clearRecentViews() {
  localStorage.removeItem(KEY)
  window.dispatchEvent(new Event('cinemate:history'))
}
