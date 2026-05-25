const dns = require("dns");
const mongoose = require("mongoose");

/**
 * Windows often fails SRV lookups (querySrv ECONNREFUSED).
 * Use Google DNS before connecting to Atlas.
 */
dns.setServers(["8.8.8.8", "8.8.4.4", "1.1.1.1"]);

function normalizeAtlasUri(uri) {
  if (!uri || !uri.startsWith("mongodb+srv://")) return uri;

  // Ensure a database name exists (required for Atlas app data)
  const match = uri.match(/^(mongodb\+srv:\/\/[^/]+)(\/[^?]*)?(\?.*)?$/);
  if (!match) return uri;

  const base = match[1];
  const path = match[2];
  const query = match[3] || "";

  if (!path || path === "/" || path === "") {
    const params = new URLSearchParams(
      query.startsWith("?") ? query.slice(1) : query
    );
    if (!params.has("retryWrites")) params.set("retryWrites", "true");
    if (!params.has("w")) params.set("w", "majority");
    const qs = params.toString();
    return `${base}/immersive_blog${qs ? `?${qs}` : ""}`;
  }

  return uri;
}

async function connectDB() {
  const uri = normalizeAtlasUri(
    process.env.MONGO_URI_STANDARD || process.env.MONGO_URI
  );

  if (!uri) {
    console.error("MONGO_URI is missing. Add it to backend/.env");
    process.exit(1);
  }

  if (uri.includes("YOUR_USERNAME") || uri.includes("YOUR_PASSWORD")) {
    console.error("Replace placeholders in backend/.env with your Atlas credentials.");
    process.exit(1);
  }

  try {
    await mongoose.connect(uri, {
      serverSelectionTimeoutMS: 20000,
      family: 4,
    });
    console.log("MongoDB connected");
  } catch (err) {
    console.error("DB connection error:", err.message);

    if (err.message.includes("querySrv") || err.message.includes("ECONNREFUSED")) {
      console.error("\nFix for querySrv ECONNREFUSED:");
      console.error("  1. In Atlas: Connect -> Drivers -> copy the FULL connection string");
      console.error("  2. Add database name: ...mongodb.net/immersive_blog?retryWrites=true&w=majority");
      console.error("  3. Or use Standard connection string in .env as MONGO_URI_STANDARD=...");
      console.error("  4. Atlas -> Network Access -> allow 0.0.0.0/0 (dev only)");
      console.error("  5. Ensure cluster is not Paused");
    }

    process.exit(1);
  }
}

module.exports = connectDB;
