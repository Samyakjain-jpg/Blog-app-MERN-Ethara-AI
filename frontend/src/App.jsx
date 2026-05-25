import { useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Provider, useDispatch, useSelector } from 'react-redux'
import { store } from './store'
import { setTheme, loadBookmarks } from './store/blogSlice'
import Header from './components/Header'
import HomePage from './pages/HomePage'
import ArticlePage from './pages/ArticlePage'

function ThemeSync({ children }) {
  const dispatch = useDispatch()
  const theme = useSelector((state) => state.blog.theme)

  useEffect(() => {
    const localTheme = localStorage.getItem('theme') || 'light'
    dispatch(setTheme(localTheme))
    dispatch(loadBookmarks())
  }, [dispatch])

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }, [theme])

  return children
}

function AppRoutes() {
  return (
    <ThemeSync>
      <div className="min-h-screen bg-white text-neutral-900 transition-colors duration-300 dark:bg-neutral-950 dark:text-neutral-50">
        <Header />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/article/:slug" element={<ArticlePage />} />
        </Routes>
      </div>
    </ThemeSync>
  )
}

export default function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </Provider>
  )
}
