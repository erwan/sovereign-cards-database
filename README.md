# Sovereign Cards Database

A small [Astro](https://astro.build/) site that lists **Sovereign: Fall of Wormwood** cards by faction (deck). Each faction page shows card names, images, and inferred types from TOML metadata under `public/cards/`.

**Live site:** [https://erwan.github.io/sovereign-cards-database/](https://erwan.github.io/sovereign-cards-database/)

This is a non-official, fan-made project. All rights to *Sovereign: Fall of Wormwood* belong to Ixion Gameworks.

## Requirements

- [Node.js](https://nodejs.org/) 18.17.1 or 20.3.0+ (as required by Astro 5)

## Local development

```bash
git clone https://github.com/erwan/sovereign-cards-database.git
cd sovereign-cards-database
npm install
npm run dev
```

The dev server prints a local URL (Astro's default is `http://localhost:4321`). Open it in a browser to browse factions and cards.

### Other commands

| Command | Purpose |
|--------|---------|
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Serve the production build locally |

The site is configured for GitHub Pages with `base: '/sovereign-cards-database'` in `astro.config.mjs`, so paths match the deployed URL. Preview behaves like production in that respect.

## Project layout (short)

- `src/pages/` — routes (home, faction pages)
- `public/cards/<faction_slug>/` — per-deck `deck.toml` and card images
- `src/lib/decks.ts` — reads and parses deck TOML at build time
