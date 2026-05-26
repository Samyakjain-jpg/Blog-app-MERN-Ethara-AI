import { useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { motion } from 'framer-motion'
import ClientFeed from '../components/ClientFeed'
import NewsletterBanner from '../components/NewsletterBanner'
import TagFilter from '../components/TagFilter'
import { loadArticles } from '../store/blogSlice'
import { seedDatabase } from '../utils/api'

export default function HomePage() {
  const dispatch = useDispatch()
  const { articles, pagination, status, error, activeTag } = useSelector(
    (state) => state.blog
  )
  const featured = articles[0]

  const loadFeed = useCallback(
    async (force = true) => {
      const result = await dispatch(
        loadArticles({ page: 1, tag: activeTag, force })
      )

      if (!loadArticles.fulfilled.match(result)) return

      const payload = result.payload
      const list = payload.fromCache
        ? null
        : payload.data?.articles

      if (!payload.fromCache && (!list || list.length === 0)) {
        try {
          await seedDatabase()
          await dispatch(loadArticles({ page: 1, tag: activeTag, force: true }))
        } catch {
          /* seed optional if articles already exist */
        }
      }
    },
    [dispatch, activeTag]
  )

  useEffect(() => {
    loadFeed(true)
  }, [loadFeed])

  const handleSeed = async () => {
    try {
      await seedDatabase()
      await dispatch(loadArticles({ page: 1, tag: activeTag, force: true }))
    } catch {
      alert('Could not seed. Is the backend running on port 5000?')
    }
  }

  const handlePage = (page) => {
    dispatch(loadArticles({ page, tag: activeTag, force: true }))
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <main className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      {featured && (
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="group relative mb-16 h-[60vh] w-full overflow-hidden rounded-2xl bg-neutral-900 sm:h-[70vh]"
        >
          {featured.coverImage && (
            <img
              src={featured.coverImage}
              alt={featured.title}
              className="absolute inset-0 h-full w-full object-cover opacity-80 transition-transform duration-700 ease-out group-hover:scale-105"
            />
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />
          <div className="absolute bottom-0 max-w-3xl p-8 md:p-12">
            <span className="rounded-full bg-emerald-500 px-3 py-1 text-xs font-medium uppercase tracking-widest text-white">
              Featured Article
            </span>
            <h1 className="mt-4 text-3xl font-bold leading-tight tracking-tight text-white md:text-5xl">
              {featured.title}
            </h1>
            <p className="mt-4 line-clamp-2 text-lg text-neutral-300">
              {featured.excerpt}
            </p>
            <div className="mt-6">
              <Link
                to={`/article/${featured.slug}`}
                className="inline-flex items-center font-semibold text-white hover:underline"
              >
                Read Deep Dive <span className="ml-2">→</span>
              </Link>
            </div>
          </div>
        </motion.section>
      )}

      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-2xl font-bold tracking-tight">Latest Stories</h2>
        {articles.length === 0 && status !== 'loading' && (
          <button
            type="button"
            onClick={handleSeed}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500"
          >
            Reload articles
          </button>
        )}
      </div>

      <TagFilter />

      {status === 'loading' && (
        <p className="py-8 text-center text-neutral-500">Loading articles...</p>
      )}
      {status === 'failed' && (
        <div className="py-8 text-center">
          <p className="text-red-500">
            {error || 'Failed to load articles. Start the backend: npm start'}
          </p>
          <button
            type="button"
            onClick={() => loadFeed(true)}
            className="mt-4 rounded-lg bg-emerald-600 px-4 py-2 text-sm text-white"
          >
            Retry
          </button>
        </div>
      )}
      {status === 'succeeded' && <ClientFeed articles={articles} />}

      {pagination.totalPages > 1 && (
        <div className="mt-12 flex justify-center gap-2">
          {Array.from({ length: pagination.totalPages }, (_, i) => i + 1).map(
            (page) => (
              <button
                key={page}
                type="button"
                onClick={() => handlePage(page)}
                className={`h-10 w-10 rounded-lg text-sm font-medium ${
                  pagination.page === page
                    ? 'bg-emerald-600 text-white'
                    : 'border border-neutral-300 dark:border-neutral-700'
                }`}
              >
                {page}
              </button>
            )
          )}
        </div>
      )}

      <NewsletterBanner />
    </main>
  )
}
