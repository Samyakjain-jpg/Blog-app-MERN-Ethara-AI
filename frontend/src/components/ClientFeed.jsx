import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { usePrefersReducedMotion } from '../hooks/usePrefersReducedMotion'

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.12 } },
}

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 100 } },
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

export default function ClientFeed({ articles }) {
  const shouldReduceMotion = usePrefersReducedMotion()

  if (!articles?.length) {
    return (
      <p className="py-12 text-center text-neutral-500">
        No articles found. Click &quot;Reload articles&quot; or restart the backend.
      </p>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial={shouldReduceMotion ? 'show' : 'hidden'}
      animate="show"
      className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3"
    >
      {articles.map((article) => (
        <motion.article
          key={article._id || article.slug}
          variants={cardVariants}
          className="flex flex-col overflow-hidden rounded-xl border border-neutral-200 bg-neutral-50 shadow-sm transition-shadow duration-200 hover:shadow-md dark:border-neutral-800 dark:bg-neutral-900"
        >
          <div className="relative h-48 w-full overflow-hidden bg-neutral-200 dark:bg-neutral-800">
            {article.coverImage ? (
              <img
                src={article.coverImage}
                alt={article.title}
                loading="lazy"
                className="h-full w-full object-cover transition-transform duration-500 hover:scale-105"
              />
            ) : (
              <div className="flex h-full items-center justify-center text-sm text-neutral-400">
                No cover image
              </div>
            )}
          </div>
          <div className="flex flex-grow flex-col p-6">
            <div className="mb-3 flex flex-wrap gap-2">
              {(article.tags || []).slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  className="text-xs font-semibold uppercase text-emerald-600 dark:text-emerald-400"
                >
                  #{tag}
                </span>
              ))}
            </div>
            <h2 className="mb-2 line-clamp-2 text-xl font-bold transition-colors hover:text-emerald-600 dark:hover:text-emerald-400">
              <Link to={`/article/${article.slug}`}>{article.title}</Link>
            </h2>
            <p className="mb-4 line-clamp-3 text-sm text-neutral-600 dark:text-neutral-400">
              {article.excerpt}
            </p>
            <div className="mt-auto flex items-center justify-between border-t border-neutral-200 pt-4 text-xs text-neutral-500 dark:border-neutral-800">
              <span>By {article.author}</span>
              <span>{formatDate(article.createdAt)}</span>
            </div>
          </div>
        </motion.article>
      ))}
    </motion.div>
  )
}
