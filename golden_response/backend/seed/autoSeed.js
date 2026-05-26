const sampleArticles = require("./sampleArticles");

async function autoSeedIfEmpty() {
  const mongoose = require("mongoose");
  const Article = mongoose.models.Article;

  if (!Article) return;

  const count = await Article.countDocuments();
  if (count > 0) {
    console.log(`Database has ${count} article(s) — skip seed`);
    return;
  }

  await Article.insertMany(sampleArticles);
  console.log(`Seeded ${sampleArticles.length} sample articles`);
}

module.exports = autoSeedIfEmpty;
