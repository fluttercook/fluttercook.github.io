import { defineConfig } from 'astro/config';

// FlutterCook — deployed to https://fluttercook.github.io (user/org Pages site → base '/')
export default defineConfig({
  site: 'https://fluttercook.github.io',
  trailingSlash: 'ignore',
  build: { format: 'directory' },
});
