# Engineering Challenge: Immersive Storytelling Blog

## The Scenario

We're building a new publishing platform geared toward deep-dive technical and creative writing. We want the reading experience to feel premium and immersive, similar to Medium, but with a heavier emphasis on fluid, hardware-accelerated micro-interactions.

Your job is to build the full-stack architecture for this platform. You'll need to handle the frontend UI, global state caching, and a secure backend for handling comments and newsletter signups.

## What You Need to Build

### 1. The Frontend (Next.js, Framer Motion, Tailwind, Redux)

- **The Reading Experience:** Build an article page layout that doesn't distract the reader. You must include a fixed reading progress bar at the top of the screen that tracks the user's scroll depth.
- **Performance-First Animations:** Use Framer Motion to handle page transitions and staggered fade-ins for the article feed. **Crucial:** Only animate properties that don't trigger layout recalculations (stick to `transform` and `opacity`). You must also respect the user's OS-level reduced motion preferences.
- **Client-Side State:** Use Redux Toolkit to manage the site's theme (light/dark mode) and cache the article feed so we aren't hammering the database every time a user clicks "Back" to the homepage.
- **Optimistic UI:** When a user leaves a comment, update the UI instantly before the server responds. If the server request fails, roll the comment back and show an error toast.

### 2. The Backend (Node.js, Express, MongoDB)

- **API Routes:** Create RESTful endpoints to fetch paginated articles, fetch a single article by its slug, post comments, and handle newsletter subscriptions.
- **Security & Sanitization (Strict):** You cannot trust user input. You must sanitize all incoming comment data on the server to prevent Cross-Site Scripting (XSS) attacks before saving it to MongoDB.
- **Rate Limiting:** Protect the POST routes (comments and newsletter) with a rate limiter to prevent spam bots from flooding the database.

## Output Expectations

Don't just give me pseudocode. I need functional, cohesive code blocks that a developer could actually piece together to run this application. Include the database schemas, the Express server setup, and the Next.js React components.
