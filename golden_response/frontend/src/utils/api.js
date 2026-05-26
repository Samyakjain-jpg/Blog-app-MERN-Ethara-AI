// In dev, Vite proxies /api → localhost:5000 (no CORS issues)
const API_URL = import.meta.env.DEV ? '' : (import.meta.env.VITE_API_URL || 'http://localhost:5000')

export async function fetchArticles({ page = 1, limit = 6, tag } = {}) {
  const params = new URLSearchParams({ page: String(page), limit: String(limit) })
  if (tag) params.set('tag', tag)

  const res = await fetch(`${API_URL}/api/articles?${params}`)
  if (!res.ok) throw new Error('Failed to fetch articles')
  const data = await res.json()
  if (!data.success) throw new Error(data.error || 'Failed to fetch articles')
  return data
}

export async function fetchArticle(slug) {
  const res = await fetch(`${API_URL}/api/articles/${slug}`)
  if (!res.ok) {
    if (res.status === 404) return null
    throw new Error('Failed to fetch article')
  }
  const data = await res.json()
  if (!data.success) throw new Error(data.error || 'Failed to fetch article')
  return data
}

export async function postComment({ articleSlug, name, body }) {
  const res = await fetch(`${API_URL}/api/comments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ articleSlug, name, body }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.error || 'Failed to post comment')
  }
  return res.json()
}

export async function subscribeNewsletter(email) {
  const res = await fetch(`${API_URL}/api/newsletter`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.error || 'Subscription failed')
  }
  return res.json()
}

export async function seedDatabase() {
  const res = await fetch(`${API_URL}/api/seed`, { method: 'POST' })
  if (!res.ok) throw new Error('Failed to seed database')
  return res.json()
}

export { API_URL }
