import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { HANDWRITTEN_RECIPES } from './src/data/handwritten-recipes.mjs';

// FlutterCook — deployed to https://fluttercook.github.io (user/org Pages site → base '/')
export default defineConfig({
  site: 'https://fluttercook.github.io',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'vi'],
    routing: { prefixDefaultLocale: false },
  },
  integrations: [
    sitemap({
      changefreq: 'weekly',
      priority: 0.7,
      lastmod: new Date(),
      // Most /recipes/<slug>/ detail pages are generated from GitHub + pub.dev
      // metadata, so they carry `noindex, follow` (see
      // src/pages/recipes/[...id].astro). Keep the sitemap consistent with
      // that: listing a noindexed URL is a contradictory signal to crawlers.
      // The /recipes/ index itself stays in — it is the hub we do want ranked,
      // and the hand-written recipes stay in because they are indexed.
      filter: (page) => {
        const m = /\/(?:vi\/)?recipes\/([^/]+)\/$/.exec(new URL(page).pathname);
        return !m || HANDWRITTEN_RECIPES.has(m[1]);
      },
    }),
  ],
});
