# Immersive Blog — Step-by-Step Build Guide

Work through the sections in order. Each section ends with a checkpoint so you can verify things work before moving on.

---

## Table of Contents

1. [Folder Setup](#1-folder-setup)  
2. [Backend — Project Init](#2-backend--project-init)  
3. [MongoDB Connection](#3-mongodb-connection)  
4. [Models (Article, Comment, Subscriber)](#4-models-article-comment-subscriber)  
5. [Security Middleware (Rate Limit + Sanitization)](#5-security-middleware-rate-limit--sanitization)  
6. [Backend Routes](#6-backend-routes)  
7. [Seed Data Endpoint (Dev)](#7-seed-data-endpoint-dev)  
8. [Test the Backend](#8-test-the-backend)  
9. [Frontend — Project Init](#9-frontend--project-init)  
10. [Tailwind Setup](#10-tailwind-setup)  
11. [Redux Store (Theme, Bookmarks, Cache)](#11-redux-store-theme-bookmarks-cache)  
12. [API Utilities](#12-api-utilities)  
13. [Home Page (Hero + Feed)](#13-home-page-hero--feed)  
14. [Article Page (Progress + Comments)](#14-article-page-progress--comments)  
15. [Optimistic Comments + Rollback](#15-optimistic-comments--rollback)  
16. [Run End-to-End](#16-run-end-to-end)  
17. [Common Errors & Fixes](#17-common-errors--fixes)  
18. [Deployment Checklist](#18-deployment-checklist)  

---

## 1. Folder Setup

```
project-root/
├── backend/
└── frontend/
```

**Checkpoint:** both folders exist.

---

## 2. Backend — Project Init

From `backend/`:

```bash
npm init -y
npm install express mongoose cors dotenv helmet express-rate-limit dompurify jsdom
npm install --save-dev nodemon
```

Add scripts:

```json
"scripts": {
  "start": "node server.js",
  "dev": "nodemon server.js"
}
```

Create `backend/.env` (use Atlas or local):

```env
PORT=5000
MONGO_URI=mongodb://127.0.0.1:27017/immersive_blog
FRONTEND_URL=http://localhost:5173
NODE_ENV=development
```

**Checkpoint:** `npm run dev` starts without “missing module” errors.

---

## 3. MongoDB Connection

In `server.js`:

- Load `.env`
- `mongoose.connect(process.env.MONGO_URI)`
- Log success/failure

**Checkpoint:** backend prints “MongoDB connected”.

---

## 4. Models (Article, Comment, Subscriber)

Create collections for:

- `Article` (title, slug, excerpt, content, coverImage, tags, author, timestamps)
- `Comment` (articleSlug, name, body, timestamps)
- `Subscriber` (email, timestamps)

**Checkpoint:** you can insert and query an `Article` from MongoDB.

---

## 5. Security Middleware (Rate Limit + Sanitization)

Requirements:

- Rate limit **POST** endpoints (comments + newsletter, optionally article creation)
- Sanitize untrusted string fields on the backend (XSS defense)

**Checkpoint:** posting comments too fast returns a 429-like error response.

---

## 6. Backend Routes

Implement:

- `GET /api/articles?page=1&limit=6&tag=react`
- `GET /api/articles/:slug` (include comments)
- `POST /api/comments` (rate limited + sanitized)
- `POST /api/newsletter` (rate limited + email validation)

**Checkpoint:** `GET /api/articles` returns JSON with an articles array.

---

## 7. Seed Data Endpoint (Dev)

Implement:

- `POST /api/seed` (disabled in production)
- Clears existing articles/comments and inserts sample articles (with cover images)

**Checkpoint:** calling seed returns “Seeded X articles”.

---

## 8. Test the Backend

Example:

```bash
curl http://localhost:5000/api/articles?page=1
curl -X POST http://localhost:5000/api/seed
```

**Checkpoint:** both calls return valid JSON.

---

## 9. Frontend — Project Init

From `frontend/`:

```bash
npm create vite@latest . -- --template react
npm install
npm install @reduxjs/toolkit react-redux framer-motion react-router-dom tailwindcss
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:5000
```

**Checkpoint:** `npm run dev` starts and shows the app.

---

## 10. Tailwind Setup

Use Tailwind v4 (Vite plugin) or standard Tailwind config, then add base styles in `src/index.css`.

**Checkpoint:** Tailwind classes apply correctly (e.g., background + text colors).

---

## 11. Redux Store (Theme, Bookmarks, Cache)

State should cover:

- theme (light/dark) + persistence
- bookmarks list (saved slugs) + persistence
- feed cache keyed by page/tag

**Checkpoint:** theme toggle persists after refresh.

---

## 12. API Utilities

Create a small API wrapper for:

- fetchArticles
- fetchArticle
- postComment
- subscribeNewsletter

**Checkpoint:** calling fetchArticles from the UI renders article cards.

---

## 13. Home Page (Hero + Feed)

Home should include:

- featured hero (first article)
- grid feed with motion-friendly transitions
- tag filter
- pagination controls

**Checkpoint:** clicking an article navigates to `/article/:slug`.

---

## 14. Article Page (Progress + Comments)

Article should include:

- scroll progress bar
- article header + content
- comment form + comment list

**Checkpoint:** progress bar moves as you scroll.

---

## 15. Optimistic Comments + Rollback

Flow:

1. Add comment immediately to UI
2. POST to backend
3. If request fails, remove optimistic comment + show error message

**Checkpoint:** if backend is stopped, submitting a comment rolls back.

---

## 16. Run End-to-End

1. Start backend (`npm run dev`)
2. Seed (`POST /api/seed`)
3. Start frontend (`npm run dev`)
4. Confirm feed renders
5. Open an article and submit a comment

**Checkpoint:** comment appears immediately and remains after refresh.

---

## 17. Common Errors & Fixes

| Error | Likely cause | Fix |
|------|-------------|-----|
| `ECONNREFUSED 27017` | Local MongoDB not running | Use Atlas URI or start MongoDB |
| `querySrv ECONNREFUSED` | Windows DNS SRV issues (Atlas) | Use public DNS / standard connection string |
| Frontend shows empty list | API unreachable / wrong port | Check `VITE_API_URL` and backend port |
| CORS errors | Backend origin mismatch | Set `FRONTEND_URL` correctly |

---

## 18. Deployment Checklist

Backend:
- Deploy to Render/Railway/Fly
- Set env vars: `MONGO_URI`, `FRONTEND_URL`

Frontend:
- Deploy to Vercel/Netlify
- Set `VITE_API_URL` to deployed backend URL

Security:
- Keep rate limiting enabled
- Do not allow wildcard CORS in production

