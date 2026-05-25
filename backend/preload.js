/**
 * Fixes Atlas querySrv ECONNREFUSED on Windows + auto-seeds empty DB.
 */
require("dotenv").config();

const dns = require("dns");
dns.setServers(["8.8.8.8", "8.8.4.4", "1.1.1.1"]);

const mongoose = require("mongoose");
const autoSeedIfEmpty = require("./seed/autoSeed");

mongoose.connection.once("open", () => {
  autoSeedIfEmpty().catch((err) =>
    console.error("Auto-seed error:", err.message)
  );
});

require("./server.js");
