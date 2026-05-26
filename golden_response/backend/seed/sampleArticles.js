module.exports = [
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
