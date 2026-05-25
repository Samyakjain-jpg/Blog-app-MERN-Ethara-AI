import { Link } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { toggleTheme } from '../store/blogSlice'

export default function Header() {
  const dispatch = useDispatch()
  const theme = useSelector((state) => state.blog.theme)
  const bookmarks = useSelector((state) => state.blog.bookmarks)

  return (
    <header className="sticky top-0 z-40 border-b border-neutral-200 bg-white/80 backdrop-blur-md dark:border-neutral-800 dark:bg-neutral-950/80">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link
          to="/"
          className="text-lg font-bold tracking-tight text-neutral-900 dark:text-white"
        >
          Immersive<span className="text-emerald-600 dark:text-emerald-400">Blog</span>
        </Link>

        <nav className="flex items-center gap-3">
          {bookmarks.length > 0 && (
            <span className="hidden text-xs text-neutral-500 sm:inline">
              {bookmarks.length} saved
            </span>
          )}
          <button
            type="button"
            onClick={() => dispatch(toggleTheme())}
            className="rounded-full border border-neutral-300 px-3 py-1.5 text-sm transition-colors hover:border-emerald-500 dark:border-neutral-700"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </nav>
      </div>
    </header>
  )
}
