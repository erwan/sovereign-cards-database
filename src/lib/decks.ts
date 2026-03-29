import fs from 'node:fs';
import path from 'node:path';
import { parse as parseYaml } from 'yaml';

export type CardType = 'unknown' | 'unit' | 'reflex' | 'augment' | 'colony';

export interface CardEntry {
  image: string;
  name: string;
  type: CardType;
}

export interface Deck {
  slug: string;
  displayName: string;
  cards: CardEntry[];
}

const CARD_TYPES = new Set<string>(['unknown', 'unit', 'reflex', 'augment', 'colony']);

export function folderToDisplayName(folder: string): string {
  return folder
    .split('_')
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

function assertCard(raw: unknown, slug: string, index: number): CardEntry {
  if (raw === null || typeof raw !== 'object' || Array.isArray(raw)) {
    throw new Error(`Invalid card at ${slug}[${index}]`);
  }
  const o = raw as Record<string, unknown>;
  if (typeof o.image !== 'string' || !o.image) {
    throw new Error(`Missing image at ${slug}[${index}]`);
  }
  if (typeof o.name !== 'string') {
    throw new Error(`Missing name at ${slug}[${index}]`);
  }
  if (typeof o.type !== 'string' || !CARD_TYPES.has(o.type)) {
    throw new Error(`Invalid type at ${slug}[${index}]: ${String(o.type)}`);
  }
  return {
    image: o.image,
    name: o.name,
    type: o.type as CardType,
  };
}

function loadDeckFromDir(slug: string, dir: string): Deck {
  const yamlPath = path.join(dir, 'deck.yaml');
  const rawText = fs.readFileSync(yamlPath, 'utf8');
  const doc = parseYaml(rawText) as unknown;
  if (doc === null || typeof doc !== 'object' || Array.isArray(doc)) {
    throw new Error(`Invalid deck.yaml root for ${slug}`);
  }
  const cardsRaw = (doc as { cards?: unknown }).cards;
  if (!Array.isArray(cardsRaw)) {
    throw new Error(`Missing cards array in ${slug}/deck.yaml`);
  }
  const cards = cardsRaw.map((c, i) => assertCard(c, slug, i));
  return {
    slug,
    displayName: folderToDisplayName(slug),
    cards,
  };
}

export function loadDecks(): Deck[] {
  const root = path.join(process.cwd(), 'public', 'cards');
  const names = fs.readdirSync(root, { withFileTypes: true });
  const decks: Deck[] = [];
  for (const ent of names) {
    if (!ent.isDirectory()) continue;
    const slug = ent.name;
    decks.push(loadDeckFromDir(slug, path.join(root, slug)));
  }
  decks.sort((a, b) => a.displayName.localeCompare(b.displayName, 'en'));
  return decks;
}
