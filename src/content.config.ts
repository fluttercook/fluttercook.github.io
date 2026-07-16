import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const recipes = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/recipes' }),
  schema: z.object({
    title: z.string(),
    package: z.string(),
    repo: z.string(),
    githubUrl: z.string(),
    category: z.string(),
    stars: z.number().default(0),
    forks: z.number().default(0),
    lastUpdate: z.string().default(''),
    pubDev: z.string().default(''),
    youtube: z.string().default(''),
    priority: z.string().default('Medium'),
    phase: z.string().default('P1'),
    trendRank: z.number().default(0),
    description: z.string().default(''),
    topics: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

const guides = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/guides' }),
  schema: z.object({
    title: z.string(),
    description: z.string().default(''),
    kind: z.string().default('YouTube'),
    topic: z.string().default(''),
    videos: z.array(z.string()).default([]),
    channels: z.array(z.string()).default([]),
    searchUrl: z.string().default(''),
    draft: z.boolean().default(false),
  }),
});

export const collections = { recipes, guides };
