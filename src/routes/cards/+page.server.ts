import { loadDecks, type CardEntry } from '$lib/decks-content';

export interface CardWithFaction extends CardEntry {
  factionSlug: string;
  factionName: string;
}

export async function load() {
  const decks = await loadDecks();

  const allCards: CardWithFaction[] = decks.flatMap((deck) =>
    deck.cards.map((card) => ({
      ...card,
      factionSlug: deck.slug,
      factionName: deck.displayName,
    }))
  );

  const allSecondaryTypes = [...new Set(
    allCards.flatMap((c) => c.type_secondary ?? [])
  )].sort();

  const typeMap: Record<string, Set<string>> = {};
  for (const card of allCards) {
    if (!card.type) continue;
    if (!typeMap[card.type]) typeMap[card.type] = new Set();
    for (const st of card.type_secondary ?? []) {
      typeMap[card.type].add(st);
    }
  }

  const validSecondaryTypesByType: Record<string, string[]> = {
    '': allSecondaryTypes,
    ...Object.fromEntries(
      Object.entries(typeMap).map(([type, set]) => [type, [...set].sort()])
    ),
  };

  return { allCards, validSecondaryTypesByType };
}
