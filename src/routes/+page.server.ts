import { loadDecks } from '$lib/decks-content.server';

export async function load() {
  const decks = await loadDecks();
  return { decks };
}
