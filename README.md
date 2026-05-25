# Immersive Storytelling Blog Platform

A simple full-stack blog with **React (Vite)**, **Redux Toolkit**, **Framer Motion**, **Tailwind CSS** on the frontend and **Node.js / Express / MongoDB** on the backend.

## Features

- Article feed with hero featured post, pagination, and tag filtering
- Single article view with scroll progress bar
- Comments (rate-limited, XSS-sanitized on the server)
- Newsletter signup
- Dark / light theme and article bookmarks (localStorage)
- Reduced-motion support for animations

## Project structure

```
├── backend/          # Express API + MongoDB
│   ├── server.js
│   └── .env.example
└── frontend/         # Vite + React app
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── store/
    │   ├── hooks/
    │   └── utils/
    └── .env.example
```

## Quick start

### 1. MongoDB

Run MongoDB locally (default: `mongodb://localhost:27017`).

### 2. Backend

```bash
cd backend
cp .env.example .env
npm install
npm run dev
```

API runs at **http://localhost:5000**

Seed sample articles (development):

```bash
curl -X POST http://localhost:5000/api/seed
```

Or click **Load sample articles** on the home page when the feed is empty.

### 3. Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

App runs at **http://localhost:5173**

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/articles` | Paginated list (`?page=1&limit=6&tag=react`) |
| GET | `/api/articles/:slug` | Article + comments |
| POST | `/api/comments` | Add comment |
| POST | `/api/newsletter` | Subscribe email |
| POST | `/api/seed` | Dev seed data |

## Environment variables

**Backend** (`backend/.env`):

```
PORT=5000
MONGO_URI=mongodb://localhost:27017/immersive_blog
FRONTEND_URL=http://localhost:5173
```

**Frontend** (`frontend/.env`):

```
VITE_API_URL=http://localhost:5000
```
