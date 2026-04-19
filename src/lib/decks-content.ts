import { DeckSchema, type CardEntry as CardEntryType } from "./schema";

export type CardEntry = CardEntryType;
export type Deck = {
  name?: string;
  description?: string;
  cards: CardEntry[];
  slug: string;
  displayName: string;
};

export const DISPLAY_TYPE_ORDER = [
  'unit',
  'colony',
  'augment',
  'reflex',
  'unknown',
] as const;

const TYPE_SECTION_HEADING: Record<string, string> = {
  unit: 'Units',
  colony: 'Colonies',
  augment: 'Augments',
  reflex: 'Reflexes',
  unknown: 'Unknown cards',
};

const TYPE_STAT_NOUN: Record<string, string> = {
  unit: 'units',
  colony: 'colonies',
  augment: 'augments',
  reflex: 'reflexes',
  unknown: 'unknown cards',
};

export function typeSectionHeading(type: string): string {
  return TYPE_SECTION_HEADING[type] || type;
}

export function typeStatNoun(type: string): string {
  return TYPE_STAT_NOUN[type] || type;
}

export function cardBlockTypeLabel(card: CardEntry): string {
  if (!card.type_secondary?.length) return '';
  return card.type_secondary.join(' / ');
}

/** 0–8 for digit costs; 9 for cost 9 or any other single-character cost. */
export function costSortKey(cost: string): number {
  if (cost.length === 1 && cost >= '0' && cost <= '8') {
    return cost.charCodeAt(0) - 48;
  }
  return 9;
}

export function compareCardsByCostThenName(a: CardEntry, b: CardEntry): number {
  const ka = costSortKey(a.cost);
  const kb = costSortKey(b.cost);
  if (ka !== kb) return ka - kb;
  const byCostChar = a.cost.localeCompare(b.cost, undefined, { sensitivity: 'base' });
  if (byCostChar !== 0) return byCostChar;
  return a.name.localeCompare(b.name, undefined, { sensitivity: 'base' });
}

export function compareCardsByNameThenCost(a: CardEntry, b: CardEntry): number {
  const byName = a.name.localeCompare(b.name, undefined, { sensitivity: 'base' });
  if (byName !== 0) return byName;
  return compareCardsByCostThenName(a, b);
}

export interface CostHistogramBin {
  label: string;
  count: number;
}

export function buildCostHistogram(cards: CardEntry[]): { bins: CostHistogramBin[]; maxCount: number } {
  const counts = new Array(10).fill(0);
  for (const c of cards) {
    counts[costSortKey(c.cost)]++;
  }
  const bins: CostHistogramBin[] = [];
  for (let i = 0; i <= 8; i++) {
    bins.push({ label: String(i), count: counts[i] });
  }
  if (counts[9] > 0) {
    bins.push({ label: 'Other', count: counts[9] });
  }
  const maxCount = Math.max(1, ...counts);
  return { bins, maxCount };
}

function folderToDisplayName(folder: string): string {
  return folder
    .split('_')
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

export async function loadDecks(): Promise<Deck[]> {
  const modules = import.meta.glob('../content/decks/*.json');
  const entries = await Promise.all(
    Object.entries(modules).map(async ([path, loader]) => {
      const mod = await loader() as { default: unknown };
      const slug = path.split('/').pop()!.replace('.json', '');
      const parsed = DeckSchema.parse(mod.default);
      const displayName = parsed.name?.trim() || folderToDisplayName(slug);
      return { ...parsed, slug, displayName };
    })
  );
  return entries.sort((a, b) => a.displayName.localeCompare(b.displayName));
}
