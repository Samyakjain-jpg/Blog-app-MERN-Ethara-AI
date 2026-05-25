import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { fetchArticles } from '../utils/api'

export const loadArticles = createAsyncThunk(
  'blog/loadArticles',
  async ({ page, tag, force = false }, { getState }) => {
    const cacheKey = `${tag || 'all'}-p${page}`
    const { blog } = getState()

    if (!force && blog.cache[cacheKey]) {
      return { fromCache: true, cacheKey }
    }

    const data = await fetchArticles({ page, tag })
    return { fromCache: false, cacheKey, data }
  }
)

const blogSlice = createSlice({
  name: 'blog',
  initialState: {
    articles: [],
    pagination: { page: 1, totalPages: 1, hasMore: false },
    status: 'idle',
    error: null,
    activeTag: null,
    cache: {},
    theme: 'light',
    bookmarks: [],
  },
  reducers: {
    toggleTheme: (state) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light'
      localStorage.setItem('theme', state.theme)
    },
    setTheme: (state, action) => {
      state.theme = action.payload
    },
    setActiveTag: (state, action) => {
      state.activeTag = action.payload
    },
    toggleBookmark: (state, action) => {
      const slug = action.payload
      if (state.bookmarks.includes(slug)) {
        state.bookmarks = state.bookmarks.filter((s) => s !== slug)
      } else {
        state.bookmarks.push(slug)
      }
      localStorage.setItem('bookmarks', JSON.stringify(state.bookmarks))
    },
    loadBookmarks: (state) => {
      const saved = localStorage.getItem('bookmarks')
      if (saved) state.bookmarks = JSON.parse(saved)
    },
    setArticlesFromServer: (state, action) => {
      state.articles = action.payload.articles
      state.pagination = action.payload.pagination
      state.status = 'succeeded'
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loadArticles.pending, (state) => {
        state.status = 'loading'
        state.error = null
      })
      .addCase(loadArticles.fulfilled, (state, action) => {
        state.status = 'succeeded'
        const { fromCache, cacheKey, data } = action.payload

        if (fromCache) {
          const cached = state.cache[cacheKey]
          state.articles = cached.articles
          state.pagination = cached.pagination
        } else {
          state.cache[cacheKey] = {
            articles: data.articles,
            pagination: data.pagination,
          }
          state.articles = data.articles
          state.pagination = data.pagination
        }
      })
      .addCase(loadArticles.rejected, (state, action) => {
        state.status = 'failed'
        state.error = action.error.message
      })
  },
})

export const {
  toggleTheme,
  setTheme,
  setActiveTag,
  toggleBookmark,
  loadBookmarks,
  setArticlesFromServer,
} = blogSlice.actions

export default blogSlice.reducer
