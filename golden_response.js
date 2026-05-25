/**
 * Golden Response: Immersive Blog API (Node.js/Express)
 * * This is the production-ready backend implementation for the benchmark.
 * It handles paginated MongoDB queries, strict XSS sanitization,
 * and rate limiting to protect the endpoints.
 * * Setup:
 * npm install express mongoose cors dotenv express-rate-limit dompurify jsdom helmet
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

// 1. Core Middleware
app.use(helmet()); // Sets secure HTTP headers automatically
app.use(cors({ origin: process.env.FRONTEND_URL || "http://localhost:3000" }));
app.use(express.json());

// 2. Security: Server-Side XSS Sanitization
// DOMPurify needs a DOM to work, so we fake one using JSDOM in Node.
const window = new JSDOM("").window;
const DOMPurify = createDOMPurify(window);

const cleanInput = (dirtyString) => {
  return DOMPurify.sanitize(dirtyString, {
    ALLOWED_TAGS: ["b", "i", "em", "strong", "a", "p"], // Only allow basic text formatting
    KEEP_CONTENT: true,
  });
};

// 3. Security: Rate Limiting
const spamLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10, // Max 10 requests per IP
  message: { error: "You are doing that too much. Please wait a bit." },
});

// 4. Database Setup (Mongoose)
mongoose
  .connect(process.env.MONGO_URI || "mongodb://localhost:27017/immersive_blog")
  .then(() => console.log("✅ MongoDB connected"))
  .catch((err) => console.error("❌ DB Error:", err));

const Article = mongoose.model(
  "Article",
  new mongoose.Schema({
    title: String,
    slug: { type: String, unique: true },
    content: String,
    tags: [String],
    createdAt: { type: Date, default: Date.now },
  }),
);

const Comment = mongoose.model(
  "Comment",
  new mongoose.Schema({
    articleSlug: { type: String, index: true },
    name: String,
    body: String,
    createdAt: { type: Date, default: Date.now },
  }),
);

// --- API Endpoints ---

// Fetch feed (with pagination)
app.get("/api/articles", async (req, res) => {
  try {
    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = 6;

    const articles = await Article.find()
      .sort({ createdAt: -1 })
      .skip((page - 1) * limit)
      .limit(limit);

    const total = await Article.countDocuments();

    res.json({
      success: true,
      articles,
      hasMore: page * limit < total,
    });
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch articles" });
  }
});

// Fetch single article and its comments
app.get("/api/articles/:slug", async (req, res) => {
  try {
    const article = await Article.findOne({ slug: req.params.slug });
    if (!article) return res.status(404).json({ error: "Article not found" });

    const comments = await Comment.find({ articleSlug: req.params.slug })
      .sort({ createdAt: -1 })
      .select("name body createdAt -_id"); // Don't expose internal Mongo IDs

    res.json({ success: true, article, comments });
  } catch (err) {
    res.status(500).json({ error: "Server error" });
  }
});

// Post a new comment (Protected & Sanitized)
app.post("/api/comments", spamLimiter, async (req, res) => {
  try {
    const { articleSlug, name, body } = req.body;

    if (!articleSlug || !name || !body) {
      return res.status(400).json({ error: "All fields are required" });
    }

    // Strip out any malicious <script> tags before touching the database
    const safeComment = await Comment.create({
      articleSlug,
      name: cleanInput(name),
      body: cleanInput(body),
    });

    res.status(201).json({ success: true, data: safeComment });
  } catch (err) {
    res.status(500).json({ error: "Could not save comment" });
  }
});

app.listen(PORT, () => console.log(`🚀 API running on port ${PORT}`));
