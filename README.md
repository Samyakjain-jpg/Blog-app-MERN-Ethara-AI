# LLM Benchmark: Full-Stack React & Node Architecture

## What is this?

This repository is a standardized benchmarking suite used to test the coding capabilities of Large Language Models (LLMs). The prompt challenges the model to design a production-ready, full-stack blogging platform.

It specifically tests a model's ability to handle complex frontend concepts (Optimistic UI updates, hardware-accelerated Framer Motion animations) and critical backend security measures (XSS sanitization in Node.js, rate limiting).

## What's Inside?

- **`prompt.md`**: The actual prompt you feed to the LLM. It's written like a real-world engineering ticket with explicit constraints.
- **`justification.md`**: The grading rubric. It breaks down exactly why an LLM passes or fails based on how it handled the edge cases.
- **`golden_response.js`**: The baseline "perfect" Node.js answer. If a model generates something close to this, it passes.

## How to Test the Golden Response

If you want to run the reference API locally to see how it works:

1.  Make sure you have Node.js and MongoDB installed on your machine.
2.  Clone this repository and open your terminal.
3.  Install the required security and server packages:
    ```bash
    npm install express mongoose cors dotenv express-rate-limit dompurify jsdom helmet
    ```
4.  Run the server:
    ```bash
    node golden_response.js
    ```
5.  The API will spin up on `http://localhost:5000`.

## How We Evaluate Models

We don't just look for working code; we look for _safe_ code. A model will fail this benchmark if it:

1.  Fails to sanitize rich-text inputs, exposing the app to Cross-Site Scripting.
2.  Suggests CSS animations that cause repaints (like animating `margin` instead of `transform`), proving a lack of frontend performance knowledge.
3.  Just writes text descriptions instead of providing functional code snippets.
