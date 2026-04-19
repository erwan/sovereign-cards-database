# Sovereign Cards Database

A [SvelteKit](https://kit.svelte.dev/) static site that lists **Sovereign: Fall of Wormwood** cards by faction (deck). Each faction page shows card names, images, and types. The all-cards page adds live search and filtering across all factions.

**Live site:** [https://erwan.github.io/sovereign-cards-database/](https://erwan.github.io/sovereign-cards-database/)

This is a non-official, fan-made project. All rights to *Sovereign: Fall of Wormwood* belong to Ixion Gameworks.

## Requirements

- [Node.js](https://nodejs.org/) 18.17.1+

## Local development

```bash
git clone https://github.com/erwan/sovereign-cards-database.git
cd sovereign-cards-database
npm install
npm run dev
```

The dev server starts at `http://localhost:5173`. Open it in a browser to browse factions and cards.

### Other commands

| Command | Purpose |
|--------|---------|
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Serve the production build locally |

The site is configured for GitHub Pages with `base: '/sovereign-cards-database'` in `svelte.config.js` (production only), so paths match the deployed URL. In dev, the base path is empty so `http://localhost:5173/` works directly.

## Project layout (short)

- `src/routes/` — pages: home (`+page`), faction detail (`factions/[slug]/+page`), all cards (`cards/+page`)
- `src/lib/components/` — Svelte components shared across pages
- `src/lib/decks-content.ts` — loads and parses deck data at build time
- `src/lib/stores.ts` — shared reactive state (view preference, lightbox)
- `src/content/decks/` — one JSON file per faction with card metadata
- `static/cards/<faction_slug>/` — card images and cover art
