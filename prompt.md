# Engineering Challenge: Immersive Storytelling Blog (Full-Stack)

## Project Overview

Build a production-ready blog platform focused on a premium reading experience and secure backend architecture.

Core product goals:
- Smooth, performance-safe animations on feed and detail pages
- Scroll-driven reading progress bar
- Reliable and secure APIs for articles, comments, and newsletter signup

---

## Tech Stack (Required)

- Frontend: React (Vite), Tailwind CSS, Redux Toolkit, Framer Motion
- Backend: Node.js, Express.js, MongoDB (Atlas or local)

---

## Project Structure (Required)

```bash
project-root/
├── frontend/
└── backend/
```

---

## Functional Requirements

### 1) Articles
- Feed endpoint with pagination and optional tag filtering
- Single article endpoint by slug
- Development-only seed endpoint to insert sample posts

### 2) Comments (Optimistic UI + Security)
- Frontend must submit comments with **optimistic UI**
- If POST fails, rollback optimistic entry and show an error state
- Backend must:
  - Rate limit comment posting
  - Sanitize untrusted comment text to prevent XSS

### 3) Newsletter
- Newsletter signup endpoint
- Rate limiting enabled
- Basic email validation

### 4) Immersive UX
- Reading progress bar fixed at top of article page
- Framer Motion transitions/stagger for feed cards
- Animate only `transform` and `opacity`
- Respect `prefers-reduced-motion`
- Persist dark/light theme

---

## Non-Functional Requirements

- Modular folder structure and readable code organization
- Clean error handling on both frontend and backend
- Safe defaults for environment variables and API behavior

---

## Evaluation Dimensions

Your solution will be evaluated on these 7 dimensions:

1. **Clarity**  
   Code and explanations are easy to follow; naming and structure are understandable.

2. **Completeness**  
   All required frontend/backend features are implemented end-to-end.

3. **Adherence**  
   Follows the required stack, structure, and constraints exactly.

4. **Efficiency**  
   Uses performant patterns (caching where reasonable, lightweight API payloads, motion-safe CSS properties).

5. **Repetitiveness**  
   Avoids unnecessary duplication in code, logic, and explanations.

6. **Human-likeness**  
   Code style and comments feel practical, maintainable, and developer-friendly (not robotic or template-spam).

7. **Accuracy**  
   APIs, state flow, error handling, and security logic are technically correct and runnable.

---

## Final Output Required

Provide runnable code (not pseudocode) for:
- Backend API (Express + MongoDB)
- Frontend UI (React + Vite)
- Environment setup files (`.env.example`)
- Clear local run instructions

The final result must be executable by a developer with minimal setup.
