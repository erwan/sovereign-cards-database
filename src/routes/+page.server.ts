import { loadDecks } from '$lib/decks-content';

export async function load() {
  const decks = await loadDecks();
  return { decks };
}
