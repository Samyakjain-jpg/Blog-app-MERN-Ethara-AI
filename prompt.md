# Immersive Storytelling Blog - Engineering Brief

You are developing a fully-realized stack blog application, consisting of a front end React-based reading experience and an Express API back end, utilizing MongoDB for storage. This should be an intuitive experience for people who browse and read an extensive story—no mockups or power point slides here!

## What we want the product to do

Readers get a home feed with pagination and optional tag filters, an article page with a scroll-linked progress indicator at the top, and a comment box that feels instant. Writers (or devs seeding data) need a way to load sample posts in development. Visitors can sign up for a newsletter. Light and dark theme should stick between visits.

Motion matters, but only where it helps: staggered card entrances on the feed, smooth progress on the article view. Stick to `transform` and `opacity` so the browser is not fighting layout on every frame. If the user has reduced motion enabled at the OS level, tone the animation down or skip it.

## Stack and layout

| Layer | Use                                                     |
| ----- | ------------------------------------------------------- |
| UI    | React with Vite, Tailwind, Redux Toolkit, Framer Motion |
| API   | Node, Express                                           |
| Data  | MongoDB (local or Atlas)                                |

```
your-repo/
  frontend/
  backend/
```

Do not swap frameworks unless you explain why and still meet every requirement below.

## Backend behavior

**Articles**

- `GET` list: pagination, optional `tag` query
- `GET` one post by `slug`, including its comments
- `POST` seed (dev only): wipe or fill sample articles so the UI has something to show

**Comments**

- `POST` to add a comment tied to an article slug
- Throttle write traffic so one IP cannot spam the database
- Clean user-supplied text before it is stored (XSS is not acceptable)

**Newsletter**

- `POST` email signup with basic format checks and the same kind of write throttling

Return JSON with consistent shapes. When something fails, send a useful status code and message—not a stack trace to the client.

## Frontend behavior

**Feed**

- Load articles from the API, show a featured hero plus a grid
- Tag filter and page controls if the API supports them
- Cache feed pages in Redux so going back from an article does not always refetch

**Article**

- Full post body, metadata, comment list
- Top progress bar driven by scroll (Framer Motion is fine)
- Bookmark toggle stored locally
- Comment form: add the comment to the UI immediately, then call the API; if the request fails, remove the optimistic row and tell the user

**Theme**

- Toggle dark/light and persist the choice

Connect the application with the API by configuring the application environment variables (such as `VITE_API_URL`). This is good enough in development environments with proxies or server-side configurations for CORS.

## How we will judge the work

It matters to us that the app actually works after `npm install`, and a quick setup message, rather than all the files being called the same as those in the tutorials. The code needs to be clear to other developers scanning through it, such as having sensible names and small modules, without copy-and-paste sections repeating the exact same thing three times. Stick to the stack mentioned above. It is preferable to have lightweight API data returned and movement without repainting the entire page. Add comments to code where it isn’t obvious.

## What to hand in

Provide a runnable codebase for `frontend/` and `backend/`, along with the `.env.example` files, and a brief explanation for starting MongoDB, the API, and the Vite development server. Answers with pseudocode only will not be considered correct.
