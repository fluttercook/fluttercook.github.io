import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// FlutterCook — deployed to https://fluttercook.github.io (user/org Pages site → base '/')
export default defineConfig({
  site: 'https://fluttercook.github.io',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
  integrations: [
    sitemap({
      changefreq: 'weekly',
      priority: 0.7,
      lastmod: new Date(),
    }),
  ],
});
