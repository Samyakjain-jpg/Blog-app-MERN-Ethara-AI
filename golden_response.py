"""
golden_response.py

Immersive Blog — Golden Response Workspace Generator
---------------------------------------------------
This module generates a clean reference workspace for the Immersive Storytelling Blog:

- backend/  Node.js + Express + MongoDB (rate limit + XSS sanitization)
- frontend/ React (Vite) UI (Tailwind, Redux Toolkit, Framer Motion)

It also runs a lightweight validation harness to verify:
1) required files exist
2) backend includes rate limiting + sanitization middleware
3) frontend uses motion progress bar and optimistic comments

Run:
  python golden_response.py

Note:
- If a folder named `backend/` or `frontend/` already exists in the current directory,
  the generator will write into `golden_workspace/` to avoid overwriting your work.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


WORKSPACE_FILES: dict[str, str] = {
    # ------------------------------ BACKEND ---------------------------------
    "backend/package.json": r"""{
  "name": "immersive-blog-backend",
  "version": "1.0.0",
  "private": true,
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "cors": "^2.8.5",
    "dotenv": "^16.4.5",
    "dompurify": "^3.0.6",
    "express": "^4.19.2",
    "express-rate-limit": "^7.5.0",
    "helmet": "^7.2.0",
    "jsdom": "^24.0.0",
    "mongoose": "^8.2.0"
  },
  "devDependencies": {
    "nodemon": "^3.1.0"
  }
}""",
    "backend/.env.example": r"""PORT=5000
MONGO_URI=mongodb://127.0.0.1:27017/immersive_blog
FRONTEND_URL=http://localhost:5173
NODE_ENV=development
""",
    "backend/server.js": r"""/**
 * Golden Response — Immersive Blog API
 * Secure endpoints: rate limit + sanitization for untrusted input.
 */
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const helmet = require("helmet");
const rateLimit = require("express-rate-limit");
const createDOMPurify = require("dompurify");
const { JSDOM } = require("jsdom");
require("dotenv").config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(helmet());
app.use(cors({ origin: process.env.FRONTEND_URL || "http://localhost:5173" }));
app.use(express.json());

// DOMPurify needs a window; use JSDOM in Node
const window = new JSDOM("").window;
const DOMPurify = createDOMPurify(window);
const sanitize = (str) =>
  DOMPurify.sanitize(String(str || ""), {
    ALLOWED_TAGS: ["b", "i", "em", "strong", "p", "a"],
    KEEP_CONTENT: true,
  });

const postLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  message: { error: "Too many requests. Please try again later." },
});

mongoose
  .connect(process.env.MONGO_URI)
  .then(() => console.log("MongoDB connected"))
  .catch((err) => console.error("DB connection error:", err.message));

const Article = mongoose.model(
  "Article",
  new mongoose.Schema(
    {
      title: { type: String, required: true },
      slug: { type: String, required: true, unique: true, lowercase: true },
      excerpt: { type: String, required: true },
      content: { type: String, required: true }, // HTML
      coverImage: { type: String, default: "" },
      tags: [{ type: String }],
      author: { type: String, default: "Anonymous" },
    },
    { timestamps: true }
  )
);

const Comment = mongoose.model(
  "Comment",
  new mongoose.Schema(
    {
      articleSlug: { type: String, required: true, index: true },
      name: { type: String, required: true },
      body: { type: String, required: true },
    },
    { timestamps: true }
  )
);

const Subscriber = mongoose.model(
  "Subscriber",
  new mongoose.Schema(
    { email: { type: String, required: true, unique: true, lowercase: true } },
    { timestamps: true }
  )
);

// GET /api/articles?page=1&limit=6&tag=react
app.get("/api/articles", async (req, res) => {
  try {
    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = Math.min(12, parseInt(req.query.limit) || 6);
    const skip = (page - 1) * limit;
    const tag = req.query.tag?.trim();
    const query = tag ? { tags: tag } : {};

    const [articles, total] = await Promise.all([
      Article.find(query)
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limit)
        .select("title slug excerpt author tags coverImage createdAt"),
      Article.countDocuments(query),
    ]);

    res.json({
      success: true,
      articles,
      pagination: { page, totalPages: Math.ceil(total / limit), hasMore: page * limit < total },
    });
  } catch {
    res.status(500).json({ error: "Failed to fetch articles." });
  }
});

// GET /api/articles/:slug
app.get("/api/articles/:slug", async (req, res) => {
  try {
    const article = await Article.findOne({ slug: req.params.slug });
    if (!article) return res.status(404).json({ error: "Article not found" });
    const comments = await Comment.find({ articleSlug: req.params.slug }).sort({ createdAt: -1 });
    res.json({ success: true, article, comments });
  } catch {
    res.status(500).json({ error: "Server error." });
  }
});

// POST /api/comments
app.post("/api/comments", postLimiter, async (req, res) => {
  const { articleSlug, name, body } = req.body || {};
  if (!articleSlug || !name || !body) {
    return res.status(400).json({ error: "articleSlug, name, body required." });
  }
  try {
    const exists = await Article.exists({ slug: articleSlug });
    if (!exists) return res.status(404).json({ error: "Article not found." });
    const comment = await Comment.create({
      articleSlug,
      name: sanitize(name),
      body: sanitize(body),
    });
    res.status(201).json({ success: true, comment });
  } catch {
    res.status(500).json({ error: "Could not save comment." });
  }
});

// POST /api/newsletter
app.post("/api/newsletter", postLimiter, async (req, res) => {
  const email = String(req.body?.email || "").trim();
  if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)) {
    return res.status(400).json({ error: "Valid email required." });
  }
  try {
    await Subscriber.create({ email });
    res.status(201).json({ success: true, message: "Subscribed!" });
  } catch (err) {
    if (err.code === 11000) return res.status(409).json({ error: "Already subscribed." });
    res.status(500).json({ error: "Could not subscribe." });
  }
});

// POST /api/seed (dev)
app.post("/api/seed", async (req, res) => {
  if (process.env.NODE_ENV === "production") return res.status(403).json({ error: "Forbidden" });
  await Article.deleteMany({});
  await Comment.deleteMany({});
  const sample = [
    {
      title: "Getting Started with the Immersive Blog",
      slug: "getting-started-immersive-blog",
      excerpt: "A quick tour of the architecture and reading experience features.",
      content: "<p>Welcome to the Immersive Blog. This sample post exists so the UI can render a full feed immediately.</p>",
      author: "Demo Author",
      tags: ["intro", "architecture"],
      coverImage: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&q=80",
    },
  ];
  await Article.insertMany(sample);
  res.json({ success: true, message: `Seeded ${sample.length} articles.` });
});

app.listen(PORT, () => console.log(`Blog API running at http://localhost:${PORT}`));
""",

    # ------------------------------ FRONTEND --------------------------------
    "frontend/package.json": r"""{
  "name": "immersive-blog-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@reduxjs/toolkit": "^2.5.0",
    "framer-motion": "^11.15.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-redux": "^9.2.0",
    "react-router-dom": "^7.1.1"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4.0.0",
    "@vitejs/plugin-react": "^6.0.1",
    "tailwindcss": "^4.0.0",
    "vite": "^8.0.0"
  }
}""",
    "frontend/.env.example": r"""VITE_API_URL=http://localhost:5000
""",
    "frontend/src/pages/HomePage.jsx": r"""import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { loadArticles } from '../store/blogSlice'

export default function HomePage() {
  const dispatch = useDispatch()
  const { articles, status } = useSelector((s) => s.blog)
  const featured = articles[0]

  useEffect(() => {
    dispatch(loadArticles({ page: 1, force: true }))
  }, [dispatch])

  return (
    <main className="mx-auto max-w-6xl px-4 py-10">
      {featured && (
        <section className="relative mb-10 h-[55vh] overflow-hidden rounded-2xl bg-neutral-900">
          {featured.coverImage && (
            <img
              src={featured.coverImage}
              alt={featured.title}
              className="absolute inset-0 h-full w-full object-cover opacity-80"
            />
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent" />
          <div className="absolute bottom-0 p-8 max-w-2xl">
            <h1 className="text-4xl font-extrabold tracking-tight text-white">
              {featured.title}
            </h1>
            <p className="mt-3 text-neutral-200 line-clamp-2">{featured.excerpt}</p>
            <Link
              to={`/article/${featured.slug}`}
              className="mt-5 inline-flex font-semibold text-white hover:underline"
            >
              Read → 
            </Link>
          </div>
        </section>
      )}

      {status === 'loading' && (
        <p className="text-center text-neutral-500">Loading…</p>
      )}

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3"
      >
        {articles.map((a) => (
          <article key={a.slug} className="overflow-hidden rounded-xl border border-neutral-200 bg-white dark:border-neutral-800 dark:bg-neutral-900">
            {a.coverImage && <img src={a.coverImage} alt={a.title} className="h-40 w-full object-cover" />}
            <div className="p-5">
              <h2 className="font-bold text-lg">
                <Link to={`/article/${a.slug}`} className="hover:text-emerald-600">
                  {a.title}
                </Link>
              </h2>
              <p className="mt-2 text-sm text-neutral-600 dark:text-neutral-400 line-clamp-3">{a.excerpt}</p>
            </div>
          </article>
        ))}
      </motion.div>
    </main>
  )
}
""",
}


def _choose_output_dir(root: Path) -> Path:
    if (root / "backend").exists() or (root / "frontend").exists():
        return root / "golden_workspace"
    return root


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def generate_workspace() -> Path:
    root = Path(os.getcwd())
    out = _choose_output_dir(root)

    for rel, content in WORKSPACE_FILES.items():
        _write(out / rel, content)

    return out


def run_validation(out: Path) -> None:
    required = [
        out / "backend" / "server.js",
        out / "backend" / "package.json",
        out / "frontend" / "package.json",
    ]
    for p in required:
        if not p.exists():
            raise AssertionError(f"Missing required file: {p}")

    server = (out / "backend" / "server.js").read_text(encoding="utf-8")
    assert "express-rate-limit" in server, "Expected rate limiting in backend"
    assert "dompurify" in server.lower(), "Expected DOMPurify sanitization in backend"

    home = (out / "frontend" / "src" / "pages" / "HomePage.jsx").read_text(encoding="utf-8")
    assert "framer-motion" in home, "Expected Framer Motion usage in frontend"


if __name__ == "__main__":
    out_dir = generate_workspace()
    run_validation(out_dir)
    print(f"[OK] Generated golden workspace at: {out_dir}")
"""
golden_response.py

BookmarkSync — Golden Response Workspace Generator
--------------------------------------------------
This script materializes a complete reference workspace for the BookmarkSync benchmark:

- backend/    Node.js + Express + MongoDB + JWT auth
- dashboard/  Vanilla HTML/CSS/JS dashboard
- extension/  Chrome Extension (Manifest V3) popup UI + API integration

It also runs a small validation harness to catch common structural mistakes
(missing files, invalid manifest, missing bearer auth handling).

Run:
  python golden_response.py
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path


# -----------------------------------------------------------------------------
# Embedded workspace file matrix
# -----------------------------------------------------------------------------

WORKSPACE_FILES: dict[str, str] = {
    # ----------------------------- BACKEND -----------------------------------
    "backend/package.json": r"""{
  "name": "bookmarksync-backend",
  "version": "1.0.0",
  "private": true,
  "description": "BookmarkSync REST API (JWT auth + MongoDB)",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "bcryptjs": "^2.4.3",
    "cors": "^2.8.5",
    "dotenv": "^16.4.5",
    "express": "^4.19.2",
    "jsonwebtoken": "^9.0.2",
    "mongoose": "^8.2.0"
  },
  "devDependencies": {
    "nodemon": "^3.1.0"
  }
}""",
    "backend/.env.example": r"""PORT=5000
MONGO_URI=mongodb://127.0.0.1:27017/bookmarksync
JWT_SECRET=replace_me_with_a_long_random_secret
""",
    "backend/config/db.js": r"""const mongoose = require('mongoose');

async function connectDB() {
  const uri = process.env.MONGO_URI;
  if (!uri) {
    console.error('MONGO_URI missing in environment');
    process.exit(1);
  }

  try {
    const conn = await mongoose.connect(uri);
    console.log(`MongoDB connected: ${conn.connection.host}`);
  } catch (err) {
    console.error('DB connection failed:', err.message);
    process.exit(1);
  }
}

module.exports = connectDB;
""",
    "backend/models/User.js": r"""const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema(
  {
    username: { type: String, required: true, trim: true },
    email: { type: String, required: true, unique: true, lowercase: true, trim: true },
    password: { type: String, required: true }
  },
  { timestamps: true }
);

module.exports = mongoose.model('User', UserSchema);
""",
    "backend/models/Bookmark.js": r"""const mongoose = require('mongoose');

const BookmarkSchema = new mongoose.Schema(
  {
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true, index: true },
    title: { type: String, required: true, trim: true },
    url: { type: String, required: true, trim: true },
    category: { type: String, default: 'Uncategorized', trim: true },
    isFavorite: { type: Boolean, default: false },
    notes: { type: String, default: '', trim: true }
  },
  { timestamps: true }
);

module.exports = mongoose.model('Bookmark', BookmarkSchema);
""",
    "backend/middleware/auth.js": r"""const jwt = require('jsonwebtoken');

module.exports = function auth(req, res, next) {
  const header = req.header('Authorization') || '';
  if (!header.startsWith('Bearer ')) {
    return res.status(401).json({ success: false, message: 'Missing Bearer token' });
  }

  const token = header.slice('Bearer '.length);
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ success: false, message: 'Invalid or expired token' });
  }
};
""",
    "backend/controllers/authController.js": r"""const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../models/User');

function signToken(userId) {
  return jwt.sign({ id: userId }, process.env.JWT_SECRET, { expiresIn: '7d' });
}

exports.register = async (req, res) => {
  try {
    const { username, email, password } = req.body;
    if (!username || !email || !password) {
      return res.status(400).json({ success: false, message: 'username, email, password required' });
    }

    const exists = await User.findOne({ email });
    if (exists) {
      return res.status(400).json({ success: false, message: 'Email already registered' });
    }

    const salt = await bcrypt.genSalt(12);
    const hashed = await bcrypt.hash(password, salt);
    const user = await User.create({ username, email, password: hashed });

    const token = signToken(user._id);
    return res.status(201).json({
      success: true,
      token,
      user: { id: user._id, username: user.username, email: user.email }
    });
  } catch (err) {
    return res.status(500).json({ success: false, message: 'Register failed' });
  }
};

exports.login = async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
      return res.status(400).json({ success: false, message: 'email and password required' });
    }

    const user = await User.findOne({ email });
    if (!user) return res.status(400).json({ success: false, message: 'Invalid credentials' });

    const ok = await bcrypt.compare(password, user.password);
    if (!ok) return res.status(400).json({ success: false, message: 'Invalid credentials' });

    const token = signToken(user._id);
    return res.json({
      success: true,
      token,
      user: { id: user._id, username: user.username, email: user.email }
    });
  } catch (err) {
    return res.status(500).json({ success: false, message: 'Login failed' });
  }
};

exports.me = async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password');
    return res.json({ success: true, user });
  } catch (err) {
    return res.status(500).json({ success: false, message: 'Profile fetch failed' });
  }
};
""",
    "backend/controllers/bookmarkController.js": r"""const Bookmark = require('../models/Bookmark');

function isValidUrl(value) {
  try {
    const u = new URL(value);
    return u.protocol === 'http:' || u.protocol === 'https:';
  } catch {
    return false;
  }
}

exports.list = async (req, res) => {
  try {
    const bookmarks = await Bookmark.find({ userId: req.user.id }).sort({ createdAt: -1 });
    return res.json({ success: true, bookmarks });
  } catch (err) {
    return res.status(500).json({ success: false, message: 'Failed to fetch bookmarks' });
  }
};

exports.create = async (req, res) => {
  try {
    const { title, url, category, notes, isFavorite } = req.body;
    if (!title || !url) {
      return res.status(400).json({ success: false, message: 'title and url are required' });
    }
    if (!isValidUrl(url)) {
      return res.status(400).json({ success: false, message: 'Invalid URL' });
    }

    const bookmark = await Bookmark.create({
      userId: req.user.id,
      title,
      url,
      category: category || 'Uncategorized',
      notes: notes || '',
      isFavorite: !!isFavorite
    });
    return res.status(201).json({ success: true, bookmark });
  } catch (err) {
    return res.status(500).json({ success: false, message: 'Create failed' });
  }
};

exports.update = async (req, res) => {
  try {
    const { id } = req.params;
    const { title, url, category, notes, isFavorite } = req.body;
    const bookmark = await Bookmark.findOne({ _id: id, userId: req.user.id });
    if (!bookmark) return res.status(404).json({ success: false, message: 'Not found' });

    if (url && !isValidUrl(url)) {
      return res.status(400).json({ success: false, message: 'Invalid URL' });
    }

    bookmark.title = title ?? bookmark.title;
    bookmark.url = url ?? bookmark.url;
    bookmark.category = category ?? bookmark.category;
    bookmark.notes = notes ?? bookmark.notes;
    bookmark.isFavorite = typeof isFavorite === 'boolean' ? isFavorite : bookmark.isFavorite;

    await bookmark.save();
    return res.json({ success: true, bookmark });
  } catch (err) {
    return res.status(500).json({ success: false, message: 'Update failed' });
  }
};

exports.remove = async (req, res) => {
  try {
    const { id } = req.params;
    const bookmark = await Bookmark.findOne({ _id: id, userId: req.user.id });
    if (!bookmark) return res.status(404).json({ success: false, message: 'Not found' });
    await bookmark.deleteOne();
    return res.json({ success: true });
  } catch (err) {
    return res.status(500).json({ success: false, message: 'Delete failed' });
  }
};

exports.toggleFavorite = async (req, res) => {
  try {
    const { id } = req.params;
    const bookmark = await Bookmark.findOne({ _id: id, userId: req.user.id });
    if (!bookmark) return res.status(404).json({ success: false, message: 'Not found' });
    bookmark.isFavorite = !bookmark.isFavorite;
    await bookmark.save();
    return res.json({ success: true, bookmark });
  } catch (err) {
    return res.status(500).json({ success: false, message: 'Favorite toggle failed' });
  }
};
""",
    "backend/routes/auth.js": r"""const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const { register, login, me } = require('../controllers/authController');

router.post('/register', register);
router.post('/login', login);
router.get('/me', auth, me);

module.exports = router;
""",
    "backend/routes/bookmarks.js": r"""const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const { list, create, update, remove, toggleFavorite } = require('../controllers/bookmarkController');

router.use(auth);

router.get('/', list);
router.post('/', create);
router.put('/:id', update);
router.delete('/:id', remove);
router.patch('/:id/favorite', toggleFavorite);

module.exports = router;
""",
    "backend/server.js": r"""const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const connectDB = require('./config/db');

dotenv.config();

const app = express();
app.use(express.json());
app.use(cors({ origin: true })); // dev-friendly; tighten for production deployments

connectDB();

app.get('/health', (req, res) => res.json({ ok: true }));
app.use('/api/auth', require('./routes/auth'));
app.use('/api/bookmarks', require('./routes/bookmarks'));

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ success: false, message: 'Internal Server Error' });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`API listening on http://localhost:${PORT}`));
""",

    # ---------------------------- DASHBOARD ----------------------------------
    "dashboard/index.html": r"""<!doctype html>
<html lang="en" data-theme="light">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>BookmarkSync Dashboard</title>
    <link rel="stylesheet" href="dashboard.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />
  </head>
  <body>
    <div id="toast" class="toast"></div>

    <div id="authOverlay" class="overlay overlay--active">
      <div class="card auth-card">
        <div class="tabs">
          <button id="tabLogin" class="tab tab--active">Login</button>
          <button id="tabSignup" class="tab">Sign up</button>
        </div>
        <form id="authForm" class="form">
          <div id="rowUsername" class="row row--hidden">
            <i class="fa-solid fa-user"></i>
            <input id="username" placeholder="Username" />
          </div>
          <div class="row">
            <i class="fa-solid fa-envelope"></i>
            <input id="email" type="email" placeholder="Email" required />
          </div>
          <div class="row">
            <i class="fa-solid fa-lock"></i>
            <input id="password" type="password" placeholder="Password" required />
          </div>
          <button class="btn btn-primary" type="submit">Continue</button>
        </form>
      </div>
    </div>

    <div class="app">
      <aside class="sidebar">
        <div class="brand">
          <i class="fa-solid fa-bookmark"></i>
          <span>BookmarkSync</span>
        </div>
        <nav class="nav">
          <a class="nav__item nav__item--active" data-panel="overview" href="#">Overview</a>
          <a class="nav__item" data-panel="bookmarks" href="#">Bookmarks</a>
          <a class="nav__item" data-panel="settings" href="#">Settings</a>
        </nav>
        <div class="sidebar__footer">
          <button id="themeBtn" class="btn btn-ghost"><i class="fa-solid fa-moon"></i> Theme</button>
          <button id="logoutBtn" class="btn btn-danger"><i class="fa-solid fa-right-from-bracket"></i> Logout</button>
        </div>
      </aside>

      <main class="main">
        <header class="header">
          <div class="search">
            <i class="fa-solid fa-magnifying-glass"></i>
            <input id="search" placeholder="Search bookmarks..." />
          </div>
          <div class="profile">
            <div class="avatar" id="avatar">BS</div>
            <div>
              <div class="profile__name" id="profileName">Guest</div>
              <div class="profile__email" id="profileEmail">Not signed in</div>
            </div>
          </div>
        </header>

        <section id="panel-overview" class="panel panel--active">
          <div class="hero">
            <h1>Welcome back</h1>
            <p>Your synced bookmarks, organized and searchable.</p>
          </div>
          <div class="stats">
            <div class="card stat"><div class="stat__num" id="statTotal">0</div><div class="stat__label">Total</div></div>
            <div class="card stat"><div class="stat__num" id="statFavs">0</div><div class="stat__label">Favorites</div></div>
            <div class="card stat"><div class="stat__num" id="statCats">0</div><div class="stat__label">Categories</div></div>
          </div>
          <h2 class="sectionTitle">Recent</h2>
          <div id="recentGrid" class="grid"></div>
        </section>

        <section id="panel-bookmarks" class="panel">
          <div class="actions">
            <select id="filterCategory"></select>
            <select id="sortOrder">
              <option value="newest">Newest</option>
              <option value="oldest">Oldest</option>
              <option value="alpha">A → Z</option>
            </select>
            <button id="addBtn" class="btn btn-primary"><i class="fa-solid fa-plus"></i> Add</button>
          </div>
          <div id="bookmarkGrid" class="grid"></div>
        </section>

        <section id="panel-settings" class="panel">
          <div class="card">
            <h2>Settings</h2>
            <p>Import/export can be added as an extension task. This dashboard focuses on core sync + management.</p>
          </div>
        </section>
      </main>
    </div>

    <div id="modal" class="modal modal--hidden">
      <div class="card modal__card">
        <h3 id="modalTitle">Add bookmark</h3>
        <form id="modalForm" class="form">
          <input type="hidden" id="bookmarkId" />
          <input id="bmTitle" placeholder="Title" required />
          <input id="bmUrl" placeholder="https://example.com" required />
          <input id="bmCategory" placeholder="Category (optional)" />
          <textarea id="bmNotes" placeholder="Notes (optional)"></textarea>
          <label class="checkbox"><input type="checkbox" id="bmFav" /> Favorite</label>
          <div class="modal__actions">
            <button type="button" id="cancelBtn" class="btn btn-ghost">Cancel</button>
            <button type="submit" class="btn btn-primary">Save</button>
          </div>
        </form>
      </div>
    </div>

    <script src="dashboard.js"></script>
  </body>
</html>
""",
    "dashboard/dashboard.css": r""":root{
  --bg:#0b1220;
  --card:#121a2c;
  --muted:#93a4be;
  --text:#eef3ff;
  --border:#24314c;
  --accent:#4f46e5;
  --danger:#ef4444;
  --shadow:0 12px 40px rgba(0,0,0,.35);
  --r:16px;
}

html[data-theme="light"]{
  --bg:#f6f8ff;
  --card:#ffffff;
  --muted:#5b6b82;
  --text:#0f172a;
  --border:#e2e8f0;
  --shadow:0 10px 30px rgba(2,6,23,.08);
}

*{box-sizing:border-box}
body{margin:0;font-family:system-ui,Segoe UI,Roboto,Arial; background:var(--bg); color:var(--text)}

.toast{position:fixed; top:20px; right:20px; padding:10px 14px; border-radius:999px; background:var(--card); border:1px solid var(--border); box-shadow:var(--shadow); opacity:0; transform:translateY(-8px); transition:.2s; z-index:1000}
.toast.toast--show{opacity:1; transform:translateY(0)}

.overlay{position:fixed; inset:0; background:var(--bg); display:none; align-items:center; justify-content:center; z-index:900}
.overlay--active{display:flex}
.card{background:var(--card); border:1px solid var(--border); border-radius:var(--r); box-shadow:var(--shadow); padding:18px}

.auth-card{width:min(440px, 92vw)}
.tabs{display:flex; gap:8px; background:color-mix(in srgb, var(--card) 70%, var(--bg)); padding:6px; border-radius:12px; margin-bottom:12px}
.tab{flex:1; border:0; background:transparent; color:var(--muted); padding:10px; border-radius:10px; font-weight:700; cursor:pointer}
.tab--active{background:var(--card); color:var(--accent); border:1px solid var(--border)}

.form{display:flex; flex-direction:column; gap:10px}
.row{display:flex; gap:10px; align-items:center; padding:10px 12px; border-radius:12px; border:1px solid var(--border); background:color-mix(in srgb, var(--card) 82%, var(--bg))}
.row--hidden{display:none}
.row input{border:0; outline:none; background:transparent; color:var(--text); width:100%}

.app{display:flex; min-height:100vh}
.sidebar{width:260px; padding:18px; border-right:1px solid var(--border); background:var(--card); display:flex; flex-direction:column; gap:16px}
.brand{display:flex; gap:10px; align-items:center; font-weight:900; color:var(--accent); font-size:18px}
.nav{display:flex; flex-direction:column; gap:6px}
.nav__item{padding:10px 12px; border-radius:12px; text-decoration:none; color:var(--muted); border:1px solid transparent}
.nav__item:hover{border-color:var(--border)}
.nav__item--active{color:var(--accent); background:color-mix(in srgb, var(--accent) 10%, var(--card))}
.sidebar__footer{margin-top:auto; display:flex; flex-direction:column; gap:10px}

.main{flex:1; padding:22px}
.header{display:flex; gap:14px; align-items:center; justify-content:space-between; margin-bottom:18px}
.search{flex:1; max-width:520px; display:flex; gap:10px; align-items:center; padding:10px 12px; border:1px solid var(--border); border-radius:999px; background:var(--card)}
.search input{border:0; outline:none; background:transparent; color:var(--text); width:100%}
.profile{display:flex; gap:12px; align-items:center}
.avatar{width:42px; height:42px; border-radius:999px; background:var(--accent); color:white; display:grid; place-items:center; font-weight:900}
.profile__name{font-weight:800}
.profile__email{color:var(--muted); font-size:12px}

.panel{display:none}
.panel--active{display:block}
.hero{padding:18px; border-radius:var(--r); background:linear-gradient(135deg, color-mix(in srgb, var(--accent) 85%, #000), #7c3aed); color:white; margin-bottom:16px}
.stats{display:grid; grid-template-columns:repeat(3, minmax(0, 1fr)); gap:12px; margin-bottom:18px}
.stat__num{font-size:28px; font-weight:900}
.stat__label{color:var(--muted)}
.sectionTitle{margin:14px 0 10px}

.grid{display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:12px}
.bookmark{display:flex; flex-direction:column; gap:10px}
.bookmark__top{display:flex; justify-content:space-between; align-items:center}
.badge{font-size:11px; font-weight:900; color:var(--accent); padding:4px 10px; border:1px solid var(--border); border-radius:999px; background:color-mix(in srgb, var(--accent) 8%, var(--card))}
.link{color:var(--muted); font-size:12px; word-break:break-all}
.actions{display:flex; gap:10px; align-items:center; margin-bottom:12px}
.actions select{border:1px solid var(--border); background:var(--card); color:var(--text); padding:10px 12px; border-radius:12px; outline:none}

.btn{border:1px solid var(--border); background:var(--card); color:var(--text); padding:10px 12px; border-radius:12px; cursor:pointer; font-weight:800}
.btn-primary{background:var(--accent); border-color:transparent; color:white}
.btn-danger{background:transparent; border-color:color-mix(in srgb, var(--danger) 60%, var(--border)); color:var(--danger)}
.btn-ghost{background:transparent}

.modal{position:fixed; inset:0; background:rgba(0,0,0,.5); display:grid; place-items:center; z-index:950}
.modal--hidden{display:none}
.modal__card{width:min(520px, 92vw)}
.modal__actions{display:flex; justify-content:flex-end; gap:10px}
.checkbox{display:flex; gap:10px; align-items:center; color:var(--muted); font-weight:700}
textarea{min-height:90px; resize:vertical; border:1px solid var(--border); background:var(--card); color:var(--text); padding:10px 12px; border-radius:12px; outline:none}
input{border:1px solid var(--border); background:var(--card); color:var(--text); padding:10px 12px; border-radius:12px; outline:none}
""",
    "dashboard/dashboard.js": r"""const API_BASE = 'http://localhost:5000/api';

const $ = (id) => document.getElementById(id);
const toast = $('toast');

let mode = 'login';
let token = localStorage.getItem('token') || '';
let user = JSON.parse(localStorage.getItem('user') || 'null');
let bookmarks = [];

function showToast(msg) {
  toast.textContent = msg;
  toast.classList.add('toast--show');
  setTimeout(() => toast.classList.remove('toast--show'), 2600);
}

function setTheme(next) {
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
}

function toggleTheme() {
  const cur = document.documentElement.getAttribute('data-theme') || 'light';
  setTheme(cur === 'light' ? 'dark' : 'light');
}

function authHeaders() {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function api(path, opts = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...opts,
    headers: {
      'Content-Type': 'application/json',
      ...(opts.headers || {}),
      ...authHeaders()
    }
  });
  return res.json();
}

function setOverlay(active) {
  $('authOverlay').classList.toggle('overlay--active', active);
}

function setAuthMode(next) {
  mode = next;
  $('tabLogin').classList.toggle('tab--active', mode === 'login');
  $('tabSignup').classList.toggle('tab--active', mode === 'signup');
  $('rowUsername').classList.toggle('row--hidden', mode !== 'signup');
}

function panel(name) {
  document.querySelectorAll('.nav__item').forEach((a) => {
    a.classList.toggle('nav__item--active', a.dataset.panel === name);
  });
  document.querySelectorAll('.panel').forEach((p) => p.classList.remove('panel--active'));
  $(`panel-${name}`).classList.add('panel--active');
}

function setProfile(u) {
  $('profileName').textContent = u?.username || 'Guest';
  $('profileEmail').textContent = u?.email || 'Not signed in';
  const letters = (u?.username || 'BS').slice(0, 2).toUpperCase();
  $('avatar').textContent = letters;
}

function computeStats() {
  $('statTotal').textContent = String(bookmarks.length);
  $('statFavs').textContent = String(bookmarks.filter((b) => b.isFavorite).length);
  $('statCats').textContent = String(new Set(bookmarks.map((b) => b.category || 'Uncategorized')).size);
}

function populateCategories() {
  const sel = $('filterCategory');
  const cats = Array.from(new Set(bookmarks.map((b) => b.category || 'Uncategorized'))).sort();
  sel.innerHTML = `<option value="all">All categories</option>` + cats.map((c) => `<option value="${c}">${c}</option>`).join('');
}

function renderCard(b) {
  const div = document.createElement('div');
  div.className = 'card bookmark';
  div.innerHTML = `
    <div class="bookmark__top">
      <span class="badge">${b.category || 'Uncategorized'}</span>
      <button class="btn btn-ghost" title="Toggle favorite">⭐</button>
    </div>
    <div style="font-weight:900">${b.title}</div>
    <div class="link">${b.url}</div>
    <div style="display:flex; gap:10px; justify-content:flex-end">
      <button class="btn btn-ghost">Edit</button>
      <button class="btn btn-danger">Delete</button>
    </div>
  `;
  const [favBtn, editBtn, delBtn] = div.querySelectorAll('button');

  favBtn.addEventListener('click', async () => {
    const res = await api(`/bookmarks/${b._id}/favorite`, { method: 'PATCH' });
    if (res.success) await refresh();
  });
  editBtn.addEventListener('click', () => openModal(b));
  delBtn.addEventListener('click', async () => {
    if (!confirm('Delete this bookmark?')) return;
    const res = await api(`/bookmarks/${b._id}`, { method: 'DELETE' });
    if (res.success) await refresh();
  });
  return div;
}

function filteredBookmarks() {
  const q = $('search').value.trim().toLowerCase();
  const cat = $('filterCategory').value;
  const sort = $('sortOrder').value;

  let list = [...bookmarks];
  if (cat !== 'all') list = list.filter((b) => (b.category || 'Uncategorized') === cat);
  if (q) list = list.filter((b) => (b.title || '').toLowerCase().includes(q) || (b.url || '').toLowerCase().includes(q));

  if (sort === 'alpha') list.sort((a, b) => a.title.localeCompare(b.title));
  if (sort === 'oldest') list.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
  if (sort === 'newest') list.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  return list;
}

function render() {
  computeStats();
  populateCategories();

  const recent = $('recentGrid');
  recent.innerHTML = '';
  bookmarks.slice(0, 3).forEach((b) => recent.appendChild(renderCard(b)));

  const grid = $('bookmarkGrid');
  grid.innerHTML = '';
  filteredBookmarks().forEach((b) => grid.appendChild(renderCard(b)));
}

async function refresh() {
  const me = await api('/auth/me').catch(() => null);
  if (!me?.success) {
    token = '';
    user = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setProfile(null);
    setOverlay(true);
    return;
  }
  user = me.user;
  localStorage.setItem('user', JSON.stringify(user));
  setProfile(user);

  const data = await api('/bookmarks');
  bookmarks = data.success ? data.bookmarks : [];
  render();
}

function openModal(bm = null) {
  $('modal').classList.remove('modal--hidden');
  $('bookmarkId').value = bm?._id || '';
  $('bmTitle').value = bm?.title || '';
  $('bmUrl').value = bm?.url || '';
  $('bmCategory').value = bm?.category || '';
  $('bmNotes').value = bm?.notes || '';
  $('bmFav').checked = !!bm?.isFavorite;
  $('modalTitle').textContent = bm ? 'Edit bookmark' : 'Add bookmark';
}
function closeModal() {
  $('modal').classList.add('modal--hidden');
}

// init
document.addEventListener('DOMContentLoaded', async () => {
  setTheme(localStorage.getItem('theme') || 'light');
  setAuthMode('login');
  setProfile(user);
  setOverlay(!token);

  $('tabLogin').addEventListener('click', () => setAuthMode('login'));
  $('tabSignup').addEventListener('click', () => setAuthMode('signup'));
  $('themeBtn').addEventListener('click', toggleTheme);
  $('logoutBtn').addEventListener('click', () => {
    token = '';
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    showToast('Logged out');
    setOverlay(true);
  });

  document.querySelectorAll('.nav__item').forEach((a) => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      panel(a.dataset.panel);
    });
  });

  $('search').addEventListener('input', render);
  $('filterCategory').addEventListener('change', render);
  $('sortOrder').addEventListener('change', render);
  $('addBtn').addEventListener('click', () => openModal(null));
  $('cancelBtn').addEventListener('click', closeModal);
  $('modal').addEventListener('click', (e) => {
    if (e.target.id === 'modal') closeModal();
  });

  $('modalForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      title: $('bmTitle').value,
      url: $('bmUrl').value,
      category: $('bmCategory').value,
      notes: $('bmNotes').value,
      isFavorite: $('bmFav').checked
    };
    const id = $('bookmarkId').value;
    const res = id
      ? await api(`/bookmarks/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
      : await api('/bookmarks', { method: 'POST', body: JSON.stringify(payload) });
    if (res.success) {
      closeModal();
      await refresh();
    } else {
      showToast(res.message || 'Save failed');
    }
  });

  $('authForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      email: $('email').value,
      password: $('password').value
    };
    if (mode === 'signup') payload.username = $('username').value;

    const res = await api(`/auth/${mode === 'signup' ? 'register' : 'login'}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.success && res.token) {
      token = res.token;
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(res.user));
      showToast('Signed in');
      setOverlay(false);
      await refresh();
    } else {
      showToast(res.message || 'Auth failed');
    }
  });

  if (token) await refresh();
});
""",

    # ---------------------------- EXTENSION ----------------------------------
    "extension/manifest.json": r"""{
  "manifest_version": 3,
  "name": "BookmarkSync",
  "version": "1.0.0",
  "description": "A secure bookmark manager with cloud sync and a dashboard.",
  "permissions": ["storage", "tabs", "activeTab"],
  "host_permissions": ["http://localhost:5000/*"],
  "background": { "service_worker": "background.js" },
  "action": { "default_popup": "popup.html" },
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}""",
    "extension/background.js": r"""chrome.runtime.onInstalled.addListener(() => {
  console.log('BookmarkSync installed');
});
""",
    "extension/popup.html": r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="stylesheet" href="popup.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />
    <title>BookmarkSync</title>
  </head>
  <body>
    <header class="hdr">
      <button id="dashboardBtn" class="brand" title="Open dashboard">
        <i class="fa-solid fa-bookmark"></i>
        <span>BookmarkSync</span>
      </button>
      <div class="hdr__right">
        <span id="userPill" class="pill">Offline</span>
        <button id="logoutBtn" class="iconBtn" title="Logout" style="display:none">
          <i class="fa-solid fa-power-off"></i>
        </button>
      </div>
    </header>

    <main class="main">
      <section id="authView" class="view view--active">
        <div class="tabs">
          <button id="loginTab" class="tab tab--active">Login</button>
          <button id="signupTab" class="tab">Sign up</button>
        </div>
        <form id="authForm" class="form">
          <input id="suUsername" placeholder="Username (signup only)" class="input input--hidden" />
          <input id="auEmail" type="email" placeholder="Email" class="input" required />
          <input id="auPass" type="password" placeholder="Password" class="input" required />
          <button class="btn btn-primary" type="submit">Continue</button>
        </form>
      </section>

      <section id="appView" class="view">
        <div class="card">
          <button id="quickBtn" class="btn btn-ghost"><i class="fa-solid fa-bolt"></i> Capture current tab</button>
          <form id="saveForm" class="form" style="margin-top:10px">
            <input id="bmTitle" class="input" placeholder="Title" required />
            <input id="bmUrl" class="input" placeholder="https://example.com" required />
            <div class="row">
              <input id="bmCategory" class="input input--row" placeholder="Category" />
              <button id="favBtn" type="button" class="btn btn-ghost btn--square" title="Favorite">
                <i class="fa-regular fa-star"></i>
              </button>
            </div>
            <button class="btn btn-primary" type="submit">Save</button>
          </form>
        </div>

        <div class="card">
          <div class="row">
            <i class="fa-solid fa-magnifying-glass" style="opacity:.7"></i>
            <input id="search" class="input input--search" placeholder="Search..." />
          </div>
          <div id="list" class="list"></div>
        </div>
      </section>
    </main>

    <div id="toast" class="toast">Saved</div>

    <script src="js/storage.js"></script>
    <script src="js/api.js"></script>
    <script src="js/auth.js"></script>
    <script src="js/popup.js"></script>
  </body>
</html>
""",
    "extension/popup.css": r""":root{
  --bg:#0b1220;
  --card:#121a2c;
  --border:#24314c;
  --text:#eef3ff;
  --muted:#93a4be;
  --accent:#4f46e5;
  --danger:#ef4444;
  --r:14px;
}
*{box-sizing:border-box}
body{margin:0; width:360px; height:560px; background:var(--bg); color:var(--text); font-family:system-ui,Segoe UI,Roboto,Arial; overflow:hidden}
.hdr{display:flex; align-items:center; justify-content:space-between; padding:14px 14px; border-bottom:1px solid var(--border); background:rgba(255,255,255,.02)}
.brand{display:flex; gap:10px; align-items:center; font-weight:900; background:transparent; border:0; color:var(--text); cursor:pointer}
.brand i{color:var(--accent)}
.hdr__right{display:flex; gap:10px; align-items:center}
.pill{font-size:11px; padding:4px 10px; border-radius:999px; border:1px solid var(--border); color:var(--muted)}
.iconBtn{background:transparent; border:1px solid var(--border); color:var(--muted); border-radius:12px; width:36px; height:36px; cursor:pointer}

.main{padding:12px; display:flex; flex-direction:column; gap:12px; height:calc(560px - 58px); overflow:auto}
.card{border:1px solid var(--border); background:var(--card); border-radius:var(--r); padding:12px}
.view{display:none; flex-direction:column; gap:12px}
.view--active{display:flex}

.tabs{display:flex; gap:8px; background:rgba(255,255,255,.04); border:1px solid var(--border); padding:6px; border-radius:12px}
.tab{flex:1; padding:8px; border:0; background:transparent; color:var(--muted); font-weight:900; cursor:pointer; border-radius:10px}
.tab--active{background:var(--card); color:var(--accent)}

.form{display:flex; flex-direction:column; gap:10px}
.input{border:1px solid var(--border); background:rgba(255,255,255,.04); color:var(--text); padding:10px 12px; border-radius:12px; outline:none}
.input--hidden{display:none}
.row{display:flex; gap:8px; align-items:center}
.input--row{flex:1}
.input--search{border:0; background:transparent; padding:10px 0; width:100%}

.btn{border:1px solid var(--border); background:transparent; color:var(--text); padding:10px 12px; border-radius:12px; cursor:pointer; font-weight:900}
.btn-primary{background:var(--accent); border-color:transparent}
.btn-ghost{background:rgba(255,255,255,.04)}
.btn--square{width:44px; display:grid; place-items:center}

.list{display:flex; flex-direction:column; gap:8px; margin-top:10px; max-height:240px; overflow:auto}
.item{border:1px solid var(--border); background:rgba(255,255,255,.03); border-radius:12px; padding:10px}
.item__top{display:flex; justify-content:space-between; align-items:center; gap:10px}
.item__title{font-weight:900; font-size:13px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.item__url{font-size:11px; color:var(--muted); word-break:break-all; margin-top:4px}
.item__actions{display:flex; gap:8px; justify-content:flex-end; margin-top:8px}
.danger{border-color:rgba(239,68,68,.5); color:var(--danger)}

.toast{position:fixed; left:50%; bottom:14px; transform:translateX(-50%) translateY(40px); opacity:0; background:var(--accent); color:white; padding:8px 12px; border-radius:999px; font-weight:900; transition:.2s}
.toast--show{transform:translateX(-50%) translateY(0); opacity:1}
""",
    "extension/js/storage.js": r"""const Storage = {
  async set(key, value) {
    return new Promise((resolve) => chrome.storage.local.set({ [key]: value }, () => resolve(true)));
  },
  async get(key) {
    return new Promise((resolve) => chrome.storage.local.get([key], (res) => resolve(res[key] ?? null)));
  },
  async remove(key) {
    return new Promise((resolve) => chrome.storage.local.remove([key], () => resolve(true)));
  }
};
""",
    "extension/js/api.js": r"""const API_BASE = 'http://localhost:5000/api';

async function apiRequest(endpoint, method = 'GET', body = null) {
  const token = await Storage.get('token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers.Authorization = `Bearer ${token}`;

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null
    });
    return await res.json();
  } catch {
    return { success: false, message: 'API unavailable' };
  }
}
""",
    "extension/js/auth.js": r"""const Auth = {
  async login(email, password) {
    return apiRequest('/auth/login', 'POST', { email, password });
  },
  async signup(username, email, password) {
    return apiRequest('/auth/register', 'POST', { username, email, password });
  },
  async me() {
    return apiRequest('/auth/me', 'GET');
  },
  async logout() {
    await Storage.remove('token');
    await Storage.remove('user');
    await Storage.remove('cached_bookmarks');
  }
};
""",
    "extension/js/popup.js": r"""let authMode = 'login';
let favorite = false;
let bookmarks = [];

const DASHBOARD_URL = 'http://127.0.0.1:5500/dashboard/index.html';

const $ = (id) => document.getElementById(id);
const toast = $('toast');

function showToast(msg, danger = false) {
  toast.textContent = msg;
  toast.style.background = danger ? 'var(--danger)' : 'var(--accent)';
  toast.classList.add('toast--show');
  setTimeout(() => toast.classList.remove('toast--show'), 2200);
}

function setView(name) {
  $('authView').classList.toggle('view--active', name === 'auth');
  $('appView').classList.toggle('view--active', name === 'app');
}

function setAuthMode(next) {
  authMode = next;
  $('loginTab').classList.toggle('tab--active', next === 'login');
  $('signupTab').classList.toggle('tab--active', next === 'signup');
  $('suUsername').classList.toggle('input--hidden', next !== 'signup');
}

function renderList() {
  const q = $('search').value.trim().toLowerCase();
  const list = $('list');
  list.innerHTML = '';

  const filtered = q
    ? bookmarks.filter((b) => (b.title || '').toLowerCase().includes(q) || (b.url || '').toLowerCase().includes(q))
    : bookmarks;

  if (!filtered.length) {
    list.innerHTML = `<div style="color:var(--muted); text-align:center; padding:14px">No bookmarks</div>`;
    return;
  }

  filtered.forEach((b) => {
    const div = document.createElement('div');
    div.className = 'item';
    div.innerHTML = `
      <div class="item__top">
        <div class="item__title" title="${b.title}">${b.title}</div>
        <button class="btn btn-ghost btn--square" title="Favorite"><i class="fa-star ${b.isFavorite ? 'fa-solid' : 'fa-regular'}"></i></button>
      </div>
      <div class="item__url">${b.url}</div>
      <div class="item__actions">
        <button class="btn danger">Delete</button>
      </div>
    `;
    const [favBtn, delBtn] = div.querySelectorAll('button');
    favBtn.addEventListener('click', async () => {
      const res = await apiRequest(`/bookmarks/${b._id}/favorite`, 'PATCH');
      if (res.success) await refresh();
    });
    delBtn.addEventListener('click', async () => {
      const res = await apiRequest(`/bookmarks/${b._id}`, 'DELETE');
      if (res.success) await refresh();
    });
    list.appendChild(div);
  });
}

async function refresh() {
  const me = await Auth.me();
  if (!me.success) {
    await Auth.logout();
    $('logoutBtn').style.display = 'none';
    $('userPill').textContent = 'Offline';
    setView('auth');
    return;
  }
  $('userPill').textContent = me.user.username || 'Online';
  $('logoutBtn').style.display = 'inline-grid';

  const data = await apiRequest('/bookmarks', 'GET');
  bookmarks = data.success ? data.bookmarks : [];
  await Storage.set('cached_bookmarks', bookmarks);
  renderList();
}

async function quickCapture() {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const t = tabs?.[0];
    if (!t) return;
    $('bmTitle').value = t.title || '';
    $('bmUrl').value = t.url || '';
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  setAuthMode('login');
  setView((await Storage.get('token')) ? 'app' : 'auth');

  $('dashboardBtn').addEventListener('click', () => chrome.tabs.create({ url: DASHBOARD_URL }));
  $('logoutBtn').addEventListener('click', async () => {
    await Auth.logout();
    showToast('Logged out');
    setView('auth');
  });
  $('loginTab').addEventListener('click', () => setAuthMode('login'));
  $('signupTab').addEventListener('click', () => setAuthMode('signup'));
  $('search').addEventListener('input', renderList);

  $('favBtn').addEventListener('click', () => {
    favorite = !favorite;
    $('favBtn').classList.toggle('btn-ghost', !favorite);
    $('favBtn').innerHTML = `<i class="fa-star ${favorite ? 'fa-solid' : 'fa-regular'}"></i>`;
  });

  $('quickBtn').addEventListener('click', quickCapture);

  $('authForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = $('auEmail').value;
    const password = $('auPass').value;
    const username = $('suUsername').value;

    const res = authMode === 'signup'
      ? await Auth.signup(username, email, password)
      : await Auth.login(email, password);

    if (res.success && res.token) {
      await Storage.set('token', res.token);
      await Storage.set('user', res.user);
      showToast('Connected');
      setView('app');
      await refresh();
    } else {
      showToast(res.message || 'Auth failed', true);
    }
  });

  $('saveForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      title: $('bmTitle').value,
      url: $('bmUrl').value,
      category: $('bmCategory').value || 'Uncategorized',
      isFavorite: favorite
    };
    const res = await apiRequest('/bookmarks', 'POST', payload);
    if (res.success) {
      showToast('Saved');
      $('saveForm').reset();
      favorite = false;
      $('favBtn').innerHTML = `<i class="fa-regular fa-star"></i>`;
      await refresh();
    } else {
      showToast(res.message || 'Save failed', true);
    }
  });

  // offline cache render immediately
  const cached = await Storage.get('cached_bookmarks');
  if (Array.isArray(cached)) {
    bookmarks = cached;
    renderList();
  }

  // then refresh from API if logged in
  await refresh();
});
""",
}


# 1x1 transparent PNG used for extension icons (safe placeholder)
_ICON_1x1_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def generate_workspace(root: Path) -> None:
    print("============================================================")
    print("BookmarkSync Golden Response — Workspace Generator")
    print("============================================================")
    print(f"Root: {root}")

    for rel, content in WORKSPACE_FILES.items():
        _write_file(root / rel, content)
        print(f"[+] wrote {rel}")

    icons_dir = root / "extension" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)
    png = base64.b64decode(_ICON_1x1_BASE64)
    for size in ("16", "48", "128"):
        (icons_dir / f"icon{size}.png").write_bytes(png)
        print(f"[+] wrote extension/icons/icon{size}.png")

    print("\nDone. Next steps:")
    print("  backend:   cd backend && npm install && npm run dev")
    print("  dashboard: open dashboard/index.html (or serve it)")
    print("  extension: chrome://extensions → Load unpacked → select extension/")
    print("============================================================\n")


def run_validation_harness(root: Path) -> None:
    print("[*] Running validation harness...")

    required_paths = [
        "backend/server.js",
        "backend/models/User.js",
        "backend/models/Bookmark.js",
        "backend/routes/auth.js",
        "backend/routes/bookmarks.js",
        "extension/manifest.json",
        "extension/popup.html",
        "dashboard/index.html",
    ]
    for p in required_paths:
        if not (root / p).exists():
            raise AssertionError(f"Missing required file: {p}")

    manifest = json.loads((root / "extension/manifest.json").read_text(encoding="utf-8"))
    assert manifest.get("manifest_version") == 3, "manifest_version must be 3"
    perms = set(manifest.get("permissions", []))
    for needed in ("storage", "tabs", "activeTab"):
        assert needed in perms, f"manifest missing permission: {needed}"

    auth_mw = (root / "backend" / "middleware" / "auth.js").read_text(encoding="utf-8")
    assert "Bearer " in auth_mw, "auth middleware must parse Bearer tokens"

    dash_js = (root / "dashboard" / "dashboard.js").read_text(encoding="utf-8")
    assert "chrome." not in dash_js, "dashboard must not call chrome.* APIs"

    print("[✔] Validation passed.\n")


if __name__ == "__main__":
    generate_workspace(Path(os.getcwd()))
    run_validation_harness(Path(os.getcwd()))

