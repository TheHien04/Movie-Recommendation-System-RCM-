import { beforeEach, describe, expect, it, vi } from 'vitest'
import { getWatchlist, isInWatchlist } from './watchlist'

const STORAGE_KEY = 'cinemate-watchlist'
const memory: Record<string, string> = {}

vi.stubGlobal('localStorage', {
  getItem: (key: string) => memory[key] ?? null,
  setItem: (key: string, value: string) => {
    memory[key] = value
  },
  removeItem: (key: string) => {
    delete memory[key]
  },
  clear: () => {
    Object.keys(memory).forEach((k) => delete memory[k])
  },
})

describe('watchlist', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('returns empty list by default', () => {
    expect(getWatchlist()).toEqual([])
  })

  it('reads persisted titles', () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(['Inception', 'Interstellar']))
    expect(getWatchlist()).toEqual(['Inception', 'Interstellar'])
    expect(isInWatchlist('Inception')).toBe(true)
    expect(isInWatchlist('Avatar')).toBe(false)
  })
})
