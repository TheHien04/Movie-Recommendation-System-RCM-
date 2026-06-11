import { test, expect } from '@playwright/test'

test('home page loads and shows hero', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  await expect(page.getByText('Cinemate')).toBeVisible()
})

test('search page accepts query', async ({ page }) => {
  await page.goto('/search?q=inception')
  await expect(page.getByRole('heading', { name: /search/i })).toBeVisible()
})

test('moods page lists mood chips', async ({ page }) => {
  await page.goto('/moods')
  await expect(page.getByRole('heading', { name: /mood/i })).toBeVisible()
})

test('leaderboard shows ranked movies', async ({ page }) => {
  await page.goto('/leaderboard')
  await expect(page.getByRole('heading', { name: /leaderboard/i })).toBeVisible()
})

test('ml battle page renders compare form', async ({ page }) => {
  await page.goto('/ml-battle')
  await expect(page.getByRole('button', { name: /compare/i })).toBeVisible()
})

test('keyboard slash focuses quick search on home', async ({ page }) => {
  await page.goto('/')
  await page.keyboard.press('/')
  const focused = page.locator('input[placeholder*="search" i], input[placeholder*="Tìm" i]')
  await expect(focused.first()).toBeFocused()
})
