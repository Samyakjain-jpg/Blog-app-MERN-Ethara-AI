# Immersive Storytelling Blog — Engineering Brief

Design a real full stack blog, where users read articles from the browser window, while articles themselves, comments on them, and subscriptions to newsletters are stored in a database accessed via an API. Everything should be simple and straightforward—the only motion used should support reading.

---

## Product goals (what and why)

| Goal | Why it matters |
|------|----------------|
| Home feed with pages and tags | Readers discover content in chunks; tags group topics without separate “category sites.” |
| Article page with scroll progress | Long posts need a sense of place; a thin top bar answers “how much is left?” without cluttering the text. |
| Comments that feel instant | Waiting on the network after every submit feels broken; the UI should update first, then confirm with the server. |
| Newsletter signup | Capture interest without accounts; email is enough for a simple list. |
| Light / dark theme that persists | Reading at night is common; the choice should survive refresh. |
| Dev-only seed data | New clones of the repo should show content immediately, without manual DB inserts. |

**Movement rules:** apply staggered entrance effects to the feed, and a smooth progress animation to the articles. Limit animations to `transform` and `opacity` transitions so that no reflow occurs on every transition frame. Respect `prefers-reduced-motion`, which will request the reduction of any movement effects if needed by the user.

---

## Why this stack

### React (UI library)

React fits a reading app that splits the screen into many small pieces (feed card, hero, comment row, theme toggle). When comment lists or filters change, you update state and the DOM diff stays predictable. For this project we are not asking for a second server-rendered framework—client-side React plus a clear API is enough.

### Vite (frontend tooling)

Vite starts fast in development and bundles efficiently for production. That keeps iteration short while you tune layout and motion. Create React App–style setups are heavier; Vite is a practical default for a Vite + React SPA.

### Tailwind CSS (for styling purposes)

Utility classes ensure that there is consistency in spacing, typography, and dark mode variations without creating many individual CSS files for the same purpose. When using Tailwind CSS for a blog having hero, cards grid, and typography, you would save time during layout development.

### Redux Toolkit (client state)

Some UI state is global: theme, saved bookmarks, and cached feed pages when the user navigates back from an article. Local `useState` alone forces prop drilling and refetching. Redux Toolkit gives a single place for that state with less boilerplate than classic Redux.

### Framer Motion (animation)

Scroll-linked progress and staggered cards are awkward in raw CSS alone. Framer Motion hooks into React and scroll position cleanly. We still limit animated properties to `transform` and `opacity` for performance.

### Node.js + Express (API)

JavaScript on the server matches the frontend language, so types and mental models stay aligned. Express is small, widely understood, and easy to mount REST routes (`GET` articles, `POST` comments). A heavier framework is unnecessary for this scope.

### MongoDB (database)

Articles, comments, and subscribers are document-shaped (nested tags, variable-length HTML body, timestamps). MongoDB stores that naturally. SQL would work too, but the brief standardizes on Mongoose + MongoDB for flexible content fields and quick local or Atlas hosting.

---

## Repository layout (why two folders)

```
your-repo/
  frontend/    → browser app (React)
  backend/     → HTTP API (Express)
```

The separation between the UI layer and the API enables the scalability of both layers separately, protects the secrets (DB URI), and follows the architecture that most production applications use. Do not combine API functionality with the React code bundle.

---

## Backend — endpoints and rationale

### Articles

| Endpoint | Purpose | Why designed this way |
|----------|---------|------------------------|
| `GET /api/articles` | List of posts, possibly tagged | No risk of loading thousands of posts at once; no need for a search system as filtering is based on tag. |
| `GET /api/articles/:slug` | One post with comments | Slugs improve URL readability; comments are bundled to avoid extra trip during first render. |
| `POST /api/seed` | Create test posts (development-only) | Data is needed for onboarding and demo purposes; make sure this endpoint is protected in production mode. |

### Comments

| Requirement | Why |
|-------------|-----|
| `POST` with `articleSlug`, `name`, `body` | Simple public comments—no login required for this brief. |
| Rate limiting on writes | Stops bots from filling the database; read endpoints stay open. |
| Sanitize text before save | Comment HTML must not become a stored XSS payload that runs for other readers. |

### Newsletter

| Requirement | Why |
|-------------|-----|
| `POST` with email | Minimal signup flow. |
| Email format validation | Rejects obvious garbage before it hits the DB. |
| Rate limiting | Same abuse protection as comments. |

**API responses:** use a consistent JSON shape (e.g. `success`, `articles`, `error`). On failure return an appropriate HTTP status and a short message—never raw stack traces to the browser.

---

## Frontend — screens and rationale

### Feed (home)

| Behavior | Why |
|----------|-----|
| Featured hero + grid | First post gets emphasis; the rest scan as cards. |
| Tag filter + pagination | Matches backend capabilities; users narrow topics without infinite scroll complexity. |
| Redux cache per page/tag | Returning from an article should not always hit the network again. |

### Article (detail)

| Behavior | Why |
|----------|-----|
| Full HTML body + metadata | Core reading experience. |
| Scroll progress bar (Framer Motion) | Tied to scroll position, not fake timers. |
| Bookmarks in `localStorage` | Personal, device-local saves without building user accounts. |
| Optimistic comments | Insert comment in UI → `POST` → on error, remove row and show message. That is the expected modern pattern for snappy forms. |

### Theme

| Behavior | Why |
|----------|-----|
| Toggle + persist | Matches reader preference; store in `localStorage` (and Redux if you already use it for theme). |

### API connection

Use `VITE_API_URL` (or a dev proxy) so the same frontend build can point at local or deployed APIs. Configure CORS on Express for the Vite origin in development.

---

## Security and operations (why these defaults)

| Practice | Reason |
|----------|--------|
| `.env` for `MONGO_URI`, `PORT`, `FRONTEND_URL` | Secrets and URLs differ per machine; never commit real `.env` files. |
| `helmet` / sensible CORS | Reduces common HTTP header issues; restrict origins in production. |
| DOMPurify (or equivalent) on the server | Browsers trust your API; cleaning input at save time is the right layer for comment text. |
| `express-rate-limit` on POST routes | Cheap protection against abuse on write paths. |

---

## What “done” looks like

- `backend/` runs with `npm install` + `npm run dev`, connects to MongoDB, serves the routes above.
- `frontend/` runs with `npm run dev`, loads the feed, opens articles, posts comments with optimistic UI, toggles theme.
- `.env.example` in both folders documents required variables.
- Short run instructions (MongoDB, seed, ports) so another developer is not guessing.

Pseudocode-only submissions do not meet the brief. The implementation must run.
