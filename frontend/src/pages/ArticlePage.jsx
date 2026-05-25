import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { motion, useScroll, useSpring } from 'framer-motion'
import { fetchArticle, postComment } from '../utils/api'
import { toggleBookmark } from '../store/blogSlice'

export default function ArticlePage() {
  const { slug } = useParams()
  const dispatch = useDispatch()
  const isBookmarked = useSelector((state) =>
    state.blog.bookmarks.includes(slug)
  )

  const [article, setArticle] = useState(null)
  const [comments, setComments] = useState([])
  const [loading, setLoading] = useState(true)
  const [name, setName] = useState('')
  const [commentBody, setCommentBody] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const { scrollYProgress } = useScroll()
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001,
  })

  useEffect(() => {
    let cancelled = false
    setLoading(true)

    fetchArticle(slug)
      .then((data) => {
        if (cancelled) return
        if (!data) {
          setArticle(null)
          return
        }
        setArticle(data.article)
        setComments(data.comments || [])
      })
      .catch(() => {
        if (!cancelled) setArticle(null)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [slug])

  const handleCommentSubmit = async (e) => {
    e.preventDefault()
    if (!name.trim() || !commentBody.trim()) return

    const savedName = name.trim()
    const savedBody = commentBody.trim()
    const optimistic = {
      _id: `temp-${Date.now()}`,
      name: savedName,
      body: savedBody,
      createdAt: new Date().toISOString(),
    }

    setComments((prev) => [optimistic, ...prev])
    setName('')
    setCommentBody('')
    setSubmitting(true)

    try {
      const res = await postComment({
        articleSlug: slug,
        name: savedName,
        body: savedBody,
      })
      setComments((prev) =>
        prev.map((c) =>
          c._id === optimistic._id
            ? { ...c, ...res.comment, _id: optimistic._id }
            : c
        )
      )
    } catch {
      setComments((prev) => prev.filter((c) => c._id !== optimistic._id))
      alert('Could not post comment. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <p className="py-24 text-center text-neutral-500">Loading article...</p>
    )
  }

  if (!article) {
    return (
      <div className="py-24 text-center">
        <h1 className="text-2xl font-bold">Article not found</h1>
        <Link to="/" className="mt-4 inline-block text-emerald-600 hover:underline">
          ← Back to home
        </Link>
      </div>
    )
  }

  return (
    <>
      <motion.div
        className="fixed top-0 left-0 right-0 z-50 h-1 origin-left bg-emerald-500"
        style={{ scaleX }}
      />

      <article className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
        {article.coverImage && (
          <div className="mb-10 overflow-hidden rounded-2xl">
            <img
              src={article.coverImage}
              alt={article.title}
              className="h-64 w-full object-cover sm:h-80"
            />
          </div>
        )}

        <header className="mb-10">
          <div className="mb-4 flex flex-wrap gap-2">
            {(article.tags || []).map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-emerald-100 px-3 py-0.5 text-xs font-semibold uppercase text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300"
              >
                #{tag}
              </span>
            ))}
          </div>
          <h1 className="mb-4 text-3xl font-extrabold tracking-tight sm:text-4xl md:text-5xl">
            {article.title}
          </h1>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">{article.author}</p>
              <p className="text-xs text-neutral-500">
                {new Date(article.createdAt).toLocaleDateString()}
              </p>
            </div>
            <button
              type="button"
              onClick={() => dispatch(toggleBookmark(slug))}
              className={`rounded-full border p-2 transition-colors ${
                isBookmarked
                  ? 'border-emerald-500 bg-emerald-500 text-white'
                  : 'border-neutral-300 dark:border-neutral-700'
              }`}
              aria-label="Bookmark article"
            >
              🔖
            </button>
          </div>
        </header>

        <div
          className="prose-blog max-w-none text-lg"
          dangerouslySetInnerHTML={{ __html: article.content }}
        />

        <hr className="my-12 border-neutral-200 dark:border-neutral-800" />

        <section>
          <h3 className="mb-6 text-2xl font-bold">
            Discussion ({comments.length})
          </h3>
          <form onSubmit={handleCommentSubmit} className="mb-8 space-y-4">
            <input
              type="text"
              placeholder="Your Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full rounded-lg border bg-transparent px-4 py-2 dark:border-neutral-800"
            />
            <textarea
              placeholder="Join the conversation..."
              rows={4}
              value={commentBody}
              onChange={(e) => setCommentBody(e.target.value)}
              required
              className="w-full rounded-lg border bg-transparent px-4 py-2 dark:border-neutral-800"
            />
            <button
              type="submit"
              disabled={submitting}
              className="rounded-lg bg-emerald-600 px-6 py-2 text-white transition-colors hover:bg-emerald-500 disabled:opacity-60"
            >
              {submitting ? 'Posting...' : 'Submit Comment'}
            </button>
          </form>

          <div className="space-y-4">
            {comments.map((c) => (
              <div
                key={c._id || `${c.name}-${c.createdAt}`}
                className="rounded-xl border border-neutral-200 bg-neutral-50 p-4 dark:border-neutral-800 dark:bg-neutral-900"
              >
                <p className="text-sm font-semibold">{c.name}</p>
                <p className="mt-1 text-neutral-600 dark:text-neutral-400">
                  {c.body}
                </p>
              </div>
            ))}
          </div>
        </section>

        <div className="mt-12">
          <Link to="/" className="text-emerald-600 hover:underline dark:text-emerald-400">
            ← All articles
          </Link>
        </div>
      </article>
    </>
  )
}
