import fs from 'node:fs';
import path from 'node:path';
import { parse as parseToml } from 'smol-toml';

export type CardType = 'unknown' | 'unit' | 'reflex' | 'augment' | 'colony';

export type CardSecondaryType =
  | 'unknown'
  | 'antigrav'
  | 'unit'
  | 'facility'
  | 'human'
  | 'xeno'
  | 'chimera'
  | 'aciereys'
  | 'mech'
  | 'reflex'
  | 'synth';

const CARD_SECONDARY_TYPES = new Set<string>([
  'unknown',
  'antigrav',
  'unit',
  'facility',
  'human',
  'xeno',
  'chimera',
  'aciereys',
  'mech',
  'reflex',
  'synth',
]);

export interface CardEntry {
  image: string;
  name: string;
  type: CardType;
  /** Single display character (e.g. digit or X). */
  cost: string;
  type_secondary?: CardSecondaryType[];
}

export interface Deck {
  slug: string;
  displayName: string;
  description: string;
  cards: CardEntry[];
}

export const DISPLAY_TYPE_ORDER: readonly CardType[] = [
  'unit',
  'colony',
  'augment',
  'reflex',
  'unknown',
] as const;

const TYPE_SECTION_HEADING: Record<CardType, string> = {
  unit: 'Units',
  colony: 'Colonies',
  augment: 'Augments',
  reflex: 'Reflexes',
  unknown: 'Unknown cards',
};

const TYPE_STAT_NOUN: Record<CardType, string> = {
  unit: 'units',
  colony: 'colonies',
  augment: 'augments',
  reflex: 'reflexes',
  unknown: 'unknown cards',
};

export function typeSectionHeading(type: CardType): string {
  return TYPE_SECTION_HEADING[type];
}

export function typeStatNoun(type: CardType): string {
  return TYPE_STAT_NOUN[type];
}

export function cardBlockTypeLabel(card: CardEntry): string {
  if (!card.type_secondary?.length) return '';
  return card.type_secondary.join(' / ');
}

function costSortKey(cost: string): number {
  if (cost.length === 1 && cost >= '0' && cost <= '9') {
    return cost.charCodeAt(0) - 48;
  }
  return 10;
}

export function compareCardsByCostThenName(a: CardEntry, b: CardEntry): number {
  const ka = costSortKey(a.cost);
  const kb = costSortKey(b.cost);
  if (ka !== kb) return ka - kb;
  const byCostChar = a.cost.localeCompare(b.cost, undefined, { sensitivity: 'base' });
  if (byCostChar !== 0) return byCostChar;
  return a.name.localeCompare(b.name, undefined, { sensitivity: 'base' });
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
  const costRaw = o.cost;
  let cost: string;
  if (typeof costRaw === 'number' && Number.isInteger(costRaw) && costRaw >= 0 && costRaw <= 9) {
    cost = String(costRaw);
  } else if (typeof costRaw === 'string' && [...costRaw].length === 1) {
    cost = costRaw;
  } else {
    throw new Error(
      `Invalid cost at ${slug}[${index}]: expected integer 0–9 or a single character, got ${String(costRaw)}`,
    );
  }
  let type_secondary: CardSecondaryType[] | undefined;
  if (o.type_secondary !== undefined && o.type_secondary !== null) {
    if (!Array.isArray(o.type_secondary) || o.type_secondary.length === 0) {
      throw new Error(`Invalid type_secondary at ${slug}[${index}]: expected non-empty array`);
    }
    const tags: CardSecondaryType[] = [];
    for (let j = 0; j < o.type_secondary.length; j++) {
      const el = o.type_secondary[j];
      if (typeof el !== 'string' || !CARD_SECONDARY_TYPES.has(el)) {
        throw new Error(`Invalid type_secondary[${j}] at ${slug}[${index}]: ${String(el)}`);
      }
      tags.push(el as CardSecondaryType);
    }
    type_secondary = tags;
  }
  return {
    image: o.image,
    name: o.name,
    type: o.type as CardType,
    cost,
    ...(type_secondary !== undefined ? { type_secondary } : {}),
  };
}

function loadDeckFromDir(slug: string, dir: string): Deck {
  const tomlPath = path.join(dir, 'deck.toml');
  const rawText = fs.readFileSync(tomlPath, 'utf8');
  const doc = parseToml(rawText) as unknown;
  if (doc === null || typeof doc !== 'object' || Array.isArray(doc)) {
    throw new Error(`Invalid deck.toml root for ${slug}`);
  }
  const root = doc as { cards?: unknown; description?: unknown; name?: unknown };
  const cardsRaw = root.cards;
  if (!Array.isArray(cardsRaw)) {
    throw new Error(`Missing cards array in ${slug}/deck.toml`);
  }
  const cards = cardsRaw.map((c, i) => assertCard(c, slug, i));
  let description = '';
  if (root.description !== undefined && root.description !== null) {
    if (typeof root.description !== 'string') {
      throw new Error(`Invalid description in ${slug}/deck.toml`);
    }
    description = root.description;
  }
  let displayName = folderToDisplayName(slug);
  if (root.name !== undefined && root.name !== null) {
    if (typeof root.name !== 'string') {
      throw new Error(`Invalid name in ${slug}/deck.toml`);
    }
    const trimmed = root.name.trim();
    if (trimmed) {
      displayName = trimmed;
    }
  }
  return {
    slug,
    displayName,
    description,
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
