## Sovereign Cards Database

This is a SvelteKit static site that serves as a database of sovereign cards, deployed to GitHub Pages. It was migrated from Astro to SvelteKit.

## Project Overview

A browsable collection of cards organized by faction. Each faction is a JSON deck file. The site provides filtering, list/gallery views, and a lightbox for full-size card images.

## Technologies

- **SvelteKit** with static adapter (prerendered, no SSR)
- **Svelte 5** (runes syntax: `$state`, `$props`, `$derived`, `$effect`, `$bindable`)
- **TypeScript** (strict mode)
- **Zod** for runtime schema validation
- **Vite** as build tool
- Output to `dist/`, base path `/sovereign-cards-database` in production

## Commands

```bash
npm run dev      # Vite dev server at http://localhost:5173
npm run build    # Build static site to dist/
npm run preview  # Serve production build locally
npm run check    # svelte-check type checking
```

## File Structure

```
src/
├── app.html
├── content/
│   └── decks/          # One JSON file per faction (10 factions)
├── lib/
│   ├── components/     # Svelte components (CardList, FilterBar, CardLightbox, etc.)
│   ├── decks-content.ts  # Data loader (import.meta.glob), sort/histogram helpers
│   ├── schema.ts         # Zod schemas for CardEntry and Deck
│   └── stores.ts         # viewPreference (localStorage), lightbox state
├── routes/
│   ├── +layout.svelte / +layout.ts   # prerender = true root layout
│   ├── +page.server.ts / +page.svelte  # Home: faction grid
│   ├── cards/
│   │   └── +page.server.ts / +page.svelte  # All-cards filterable browser
│   └── factions/[slug]/
│       └── +page.server.ts / +page.svelte  # Faction detail with cost histogram
└── styles/             # CSS files imported per page/component

static/               # Static assets including card images in static/cards/<slug>/
scripts/
└── ocr_card_headers.py  # Python/Tesseract OCR to extract card metadata from images
```

## Data Model

Cards (`CardEntry`): `image`, `name`, `type` (unit/reflex/augment/colony/unknown), `cost` (0–8 or 'X'), `type_secondary` (array).

Decks (`Deck`): optional `name`/`description`, array of `cards`.

All deck JSON files live in `src/content/decks/` and are loaded at build time via `import.meta.glob`.

## Key Notes

- All routes are statically prerendered — there is no server-side runtime.
- The base path is empty in dev and `/sovereign-cards-database` in production (GitHub Pages).
- Card images live in `static/cards/<slug>/` and are referenced with the base path prefix.
- The OCR script (`scripts/ocr_card_headers.py`) requires Tesseract on PATH; it writes JSON (not TOML).
