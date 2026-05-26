# Engineering Challenge: Immersive Storytelling Blog (Full‑Stack)

## Project Overview

Build a premium blog platform that feels “immersive” during reading:

- Smooth, performance‑safe animations on the feed and article pages
- A top reading progress bar driven by scroll position
- A secure backend for articles, comments, and newsletter signup

---

## Tech Stack

- Frontend: React (Vite), Tailwind CSS, Redux Toolkit, Framer Motion
- Backend: Node.js, Express.js, MongoDB (Atlas or local)

---

## Project Structure

```
project-root/
├── frontend/
└── backend/
```

---

## FEATURES REQUIRED

## 1. ARTICLES

- Feed endpoint with pagination and optional tag filtering
- Single article endpoint by slug
- Seed endpoint (development only) to insert sample posts

---

## 2. COMMENTS (Optimistic UI + Security)

- Frontend must post comments with **optimistic UI**
- If the POST fails, rollback and show an error message
- Backend must:
  - Rate limit comment posting
  - Sanitize comment content to prevent XSS

---

## 3. NEWSLETTER

- Newsletter signup endpoint
- Rate limited to prevent spam
- Basic email validation

---

## 4. IMMERSIVE UI REQUIREMENTS

- Article reading progress bar at top of page
- Use Framer Motion for card transitions/stagger on feed
- Only animate `transform` and `opacity`
- Respect `prefers-reduced-motion`
- Dark/light theme toggle persisted in storage

---

## 5. FINAL OUTPUT REQUIRED

Provide functional code for:

- Backend API (Express + MongoDB)
- Frontend UI (React + Vite)
- Environment setup files (`.env.example`)
- Clear run instructions

Do not respond with pseudocode only. The solution must be runnable.
