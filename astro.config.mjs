// @ts-check
import { defineConfig } from 'astro/config';
import { resolve } from 'path';

// https://astro.build/config
export default defineConfig({
  site: 'https://erwan.github.io',
  base: '/sovereign-cards-database',
  vite: {
    resolve: {
      alias: {
        '@content': resolve('./src/content/decks'),
      },
    },
  },
});
