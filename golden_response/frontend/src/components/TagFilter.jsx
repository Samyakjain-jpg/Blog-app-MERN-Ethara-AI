import { useDispatch, useSelector } from 'react-redux'
import { loadArticles, setActiveTag } from '../store/blogSlice'

const POPULAR_TAGS = [
  'react',
  'nodejs',
  'mongodb',
  'security',
  'frontend',
  'backend',
]

export default function TagFilter() {
  const dispatch = useDispatch()
  const activeTag = useSelector((state) => state.blog.activeTag)

  const handleTag = (tag) => {
    const next = activeTag === tag ? null : tag
    dispatch(setActiveTag(next))
    dispatch(loadArticles({ page: 1, tag: next, force: true }))
  }

  return (
    <div className="mb-8 flex flex-wrap gap-2">
      <button
        type="button"
        onClick={() => handleTag(null)}
        className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
          !activeTag
            ? 'bg-emerald-600 text-white'
            : 'border border-neutral-300 dark:border-neutral-700'
        }`}
      >
        All
      </button>
      {POPULAR_TAGS.map((tag) => (
        <button
          key={tag}
          type="button"
          onClick={() => handleTag(tag)}
          className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
            activeTag === tag
              ? 'bg-emerald-600 text-white'
              : 'border border-neutral-300 dark:border-neutral-700'
          }`}
        >
          #{tag}
        </button>
      ))}
    </div>
  )
}
