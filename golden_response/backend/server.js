/**
 * Blog API Server (Express + MongoDB)
 * Features: XSS sanitization, rate limiting, pagination
 * Run: npm install && node server.js
 */

const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const helmet = require("helmet");
const rateLimit = require("express-rate-limit");
const createDOMPurify = require("dompurify");
const { JSDOM } = require("jsdom");
require("dotenv").config();

const connectDB = require("./config/db");

const app = express();
const PORT = process.env.PORT || 5000;

// ── Middleware ──────────────────────────────────────────────────────────────
app.use(helmet());
const allowedOrigins = [
  process.env.FRONTEND_URL,
  "http://localhost:3000",
  "http://localhost:5173",
].filter(Boolean);

app.use(
  cors({
    origin: (origin, callback) => {
      if (!origin || allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(null, allowedOrigins[0] || "http://localhost:5173");
      }
    },
  })
);
app.use(express.json());

// ── XSS Sanitizer (DOMPurify needs a fake DOM in Node.js) ──────────────────
const window = new JSDOM("").window;
const DOMPurify = createDOMPurify(window);

const sanitize = (str) =>
  DOMPurify.sanitize(str, {
    ALLOWED_TAGS: ["b", "i", "em", "strong", "p"],
    KEEP_CONTENT: true,
  });

// ── Rate Limiter (POST routes only) ────────────────────────────────────────
const postLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10,
  message: { error: "Too many requests. Please wait a moment." },
});

// ── MongoDB Connection ──────────────────────────────────────────────────────
mongoose
  .connect(process.env.MONGO_URI || "mongodb://localhost:27017/blog_db")
  .then(() => console.log("✅ MongoDB connected"))
  .catch((err) => console.error("❌ DB connection error:", err.message));

// ── Schemas & Models ───────────────────────────────────────────────────────
const articleSchema = new mongoose.Schema({
  title: { type: String, required: true, trim: true },
  slug: { type: String, required: true, unique: true, lowercase: true },
  excerpt: { type: String, required: true },
  content: { type: String, required: true },
  author: { type: String, default: "Anonymous" },
  tags: [{ type: String, trim: true }],
  coverImage: { type: String, default: "" },
  createdAt: { type: Date, default: Date.now },
});

const commentSchema = new mongoose.Schema({
  articleSlug: { type: String, required: true, index: true },
  name: { type: String, required: true, trim: true },
  body: { type: String, required: true },
  createdAt: { type: Date, default: Date.now },
});

const subscriberSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true, lowercase: true },
  subscribedAt: { type: Date, default: Date.now },
});

const Article = mongoose.model("Article", articleSchema);
const Comment = mongoose.model("Comment", commentSchema);
const Subscriber = mongoose.model("Subscriber", subscriberSchema);

// ── Routes ─────────────────────────────────────────────────────────────────

// GET /api/articles — paginated article feed (optional tag filter)
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
      pagination: {
        page,
        totalPages: Math.ceil(total / limit),
        hasMore: page * limit < total,
      },
    });
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch articles." });
  }
});

// GET /api/articles/:slug — single article with comments
app.get("/api/articles/:slug", async (req, res) => {
  try {
    const article = await Article.findOne({ slug: req.params.slug });
    if (!article) return res.status(404).json({ error: "Article not found." });

    const comments = await Comment.find({ articleSlug: req.params.slug })
      .sort({ createdAt: -1 })
      .select("name body createdAt -_id");

    res.json({ success: true, article, comments });
  } catch (err) {
    res.status(500).json({ error: "Server error." });
  }
});

// POST /api/articles — create a new article
app.post("/api/articles", postLimiter, async (req, res) => {
  try {
    const { title, slug, excerpt, content, author, tags, coverImage } =
      req.body;

    if (!title || !slug || !excerpt || !content) {
      return res
        .status(400)
        .json({ error: "title, slug, excerpt, and content are required." });
    }

    const article = await Article.create({
      title: sanitize(title),
      slug,
      excerpt: sanitize(excerpt),
      content: sanitize(content),
      author: author ? sanitize(author) : "Anonymous",
      tags: Array.isArray(tags) ? tags.map(sanitize) : [],
      coverImage: coverImage || "",
    });

    res.status(201).json({ success: true, article });
  } catch (err) {
    if (err.code === 11000) {
      return res.status(409).json({ error: "Slug already exists." });
    }
    res.status(500).json({ error: "Could not create article." });
  }
});

// POST /api/comments — post a comment (rate limited + sanitized)
app.post("/api/comments", postLimiter, async (req, res) => {
  try {
    const { articleSlug, name, body } = req.body;

    if (!articleSlug || !name || !body) {
      return res
        .status(400)
        .json({ error: "articleSlug, name, and body are required." });
    }

    // Verify the article exists before saving a comment
    const articleExists = await Article.exists({ slug: articleSlug });
    if (!articleExists) {
      return res.status(404).json({ error: "Article not found." });
    }

    const comment = await Comment.create({
      articleSlug,
      name: sanitize(name),
      body: sanitize(body),
    });

    res.status(201).json({
      success: true,
      comment: {
        name: comment.name,
        body: comment.body,
        createdAt: comment.createdAt,
      },
    });
  } catch (err) {
    res.status(500).json({ error: "Could not save comment." });
  }
});

// POST /api/newsletter — newsletter signup (rate limited)
app.post("/api/newsletter", postLimiter, async (req, res) => {
  try {
    const { email } = req.body;

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return res.status(400).json({ error: "A valid email is required." });
    }

    await Subscriber.create({ email: email.toLowerCase() });
    res
      .status(201)
      .json({ success: true, message: "Subscribed successfully!" });
  } catch (err) {
    if (err.code === 11000) {
      return res.status(409).json({ error: "Email already subscribed." });
    }
    res.status(500).json({ error: "Could not subscribe." });
  }
});

// ── Seed endpoint (dev only) ───────────────────────────────────────────────
app.post("/api/seed", async (req, res) => {
  if (process.env.NODE_ENV === "production") {
    return res.status(403).json({ error: "Forbidden in production." });
  }

  await Article.deleteMany({});
  await Comment.deleteMany({});

  const sampleArticles = [
    {
      title: "Getting Started with MERN Stack",
      slug: "getting-started-mern-stack",
      excerpt:
        "A practical guide to building full-stack apps with MongoDB, Express, React, and Node.",
      content:
        "<p>The MERN stack is one of the most popular choices for building modern web applications. It covers the full spectrum from database to UI using a single language: JavaScript.</p><p>In this guide, we'll walk through setting up your first MERN project step by step.</p>",
      author: "Alex Johnson",
      tags: ["mern", "nodejs", "react", "mongodb"],
      coverImage:
        "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&q=80",
    },
    {
      title: "Understanding XSS Attacks and How to Prevent Them",
      slug: "xss-attacks-prevention",
      excerpt:
        "Cross-Site Scripting is one of the most common web vulnerabilities. Learn how to defend against it.",
      content:
        "<p>XSS attacks occur when an attacker injects malicious scripts into content from a trusted website. These scripts can steal cookies, session tokens, or redirect users to malicious sites.</p><p>On the server side, always sanitize user input using libraries like DOMPurify before storing it in your database.</p>",
      author: "Sarah Chen",
      tags: ["security", "xss", "nodejs", "backend"],
      coverImage:
        "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800&q=80",
    },
    {
      title: "React State Management with Redux Toolkit",
      slug: "react-redux-toolkit-guide",
      excerpt:
        "Redux Toolkit simplifies Redux dramatically. Here's how to manage global state the modern way.",
      content:
        "<p>Redux Toolkit (RTK) is the official, opinionated toolset for Redux. It eliminates the boilerplate that made classic Redux so tedious to set up.</p><p>With <strong>createSlice</strong>, you define reducers and actions together, and RTK auto-generates action creators for you.</p>",
      author: "Marcus Lee",
      tags: ["react", "redux", "frontend", "state-management"],
      coverImage:
        "https://images.unsplash.com/photo-1633356122102-3fe601e05bd2?w=800&q=80",
    },
    {
      title: "Building Immersive UI with Framer Motion",
      slug: "framer-motion-immersive-ui",
      excerpt:
        "Smooth animations and micro-interactions that respect accessibility and performance.",
      content:
        "<p>Framer Motion brings declarative animations to React. Combine staggered children, spring physics, and scroll-linked effects for a polished reading experience.</p><p>Always pair motion with <strong>prefers-reduced-motion</strong> so every reader can enjoy your blog comfortably.</p>",
      author: "Jordan Kim",
      tags: ["react", "animation", "frontend", "accessibility"],
      coverImage:
        "https://images.unsplash.com/photo-1618477388954-7852f8964553?w=800&q=80",
    },
    {
      title: "MongoDB Schema Design for Content Platforms",
      slug: "mongodb-schema-content-platforms",
      excerpt:
        "Model articles, comments, and subscribers with indexes that scale as your audience grows.",
      content:
        "<p>Start with clear document boundaries: articles own their metadata, comments reference articles by slug, and subscribers stay in a separate collection.</p><p>Index fields you query often—like <strong>articleSlug</strong> on comments—for fast lookups at scale.</p>",
      author: "Priya Nair",
      tags: ["mongodb", "backend", "database", "architecture"],
      coverImage:
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&q=80",
    },
    {
      title: "Tailwind CSS for Editorial Layouts",
      slug: "tailwind-editorial-layouts",
      excerpt:
        "Utility-first styling for hero sections, card grids, and typography-focused article pages.",
      content:
        "<p>Tailwind's design tokens keep spacing and color consistent across light and dark themes. Use <strong>prose</strong> classes for long-form reading comfort.</p><p>Dark mode with <strong>class</strong> strategy pairs perfectly with Redux-persisted theme toggles.</p>",
      author: "Elena Rossi",
      tags: ["tailwind", "css", "frontend", "design"],
      coverImage:
        "https://images.unsplash.com/photo-1507721999472-8ed4421c4af2?w=800&q=80",
    },
  ];

  await Article.insertMany(sampleArticles);
  res.json({
    success: true,
    message: `Seeded ${sampleArticles.length} articles.`,
  });
});

// ── Start Server ───────────────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`🚀 Blog API running at http://localhost:${PORT}`);
});
