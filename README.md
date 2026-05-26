# Immersive Storytelling Blog

A full-stack blog platform with an immersive reading experience (progress bar + motion-friendly UI) and a secure API for comments and newsletter signup.

---

## Project Structure

```
immersive-blog/
├── backend/                  # Node.js + Express + MongoDB API
│   ├── server.js
│   ├── package.json
│   └── .env.example
│
└── frontend/                 # React (Vite) UI
    ├── src/
    ├── package.json
    └── .env.example
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite, Tailwind CSS, Redux Toolkit, Framer Motion |
| Backend | Node.js, Express.js |
| Database | MongoDB (Atlas or local) |
| Security | Rate limiting + server-side XSS sanitization |

---

## Features

- **Article feed** — featured hero + grid, pagination, tag filter
- **Article view** — reading progress bar, bookmarks, comments
- **Comments** — optimistic UI (frontend) + rate limited + sanitized (backend)
- **Newsletter** — signup endpoint with rate limiting
- **Theme** — light/dark with persistence

---

## Prerequisites

- Node.js 18+
- MongoDB (local) or MongoDB Atlas

---

## Quick Start

### 1) Backend

```bash
cd backend
cp .env.example .env
npm install
npm run dev
```

API runs at `http://localhost:5000`.

Seed sample articles (development):

```bash
curl -X POST http://localhost:5000/api/seed
```

### 2) Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Vite runs at the URL it prints (usually `http://localhost:5173`).

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/articles?page=1&limit=6&tag=react` | Paginated feed (optional tag) |
| GET | `/api/articles/:slug` | Single article + comments |
| POST | `/api/comments` | Add comment (rate limited + sanitized) |
| POST | `/api/newsletter` | Newsletter signup (rate limited) |
| POST | `/api/seed` | Seed sample articles (dev only) |

---

## Environment Variables

Backend (`backend/.env`):

```env
PORT=5000
MONGO_URI=mongodb://127.0.0.1:27017/immersive_blog
FRONTEND_URL=http://localhost:5173
NODE_ENV=development
```

Frontend (`frontend/.env`):

```env
VITE_API_URL=http://localhost:5000
```

---

## Build Guide (step-by-step)

See `BUILD_GUIDE.md`.

---

## Security Notes

- Never commit `.env` secrets
- Keep rate limits enabled on write endpoints
- Always sanitize untrusted text before storing or rendering
