// Recipes written by hand rather than generated.
//
// The other 500 recipes are assembled from GitHub and pub.dev metadata, so both
// recipe routes serve them `noindex, follow` with ads off, and astro.config.mjs
// keeps them out of the sitemap — Google Publisher Policies forbid monetising
// pages built from someone else's content without adding value of your own, and
// "low value content" is the most common AdSense rejection for templated pages.
//
// The slugs below are the exception: original reviews with first-hand analysis,
// real install steps verified against each project, and an honest read on where
// each one falls short. That is the added value the policy asks for, so these
// pages are indexed and carry ads like the rest of the hand-written site.
//
// This list is the single source of truth. Both recipe routes and the sitemap
// filter import it, so a slug added here is indexed everywhere at once — and
// removing a slug puts that page straight back with the generated 500. Only add
// a slug you actually wrote.
export const HANDWRITTEN_RECIPES = new Set([
  'adaptive-platform-ui',
  'dart-mcp',
  'denial',
  'flutter-init',
  'flutter-skill',
  'flutter-zero',
  'maidkit',
  'rejourney',
  'simvyn',
  'tapflow',
]);
