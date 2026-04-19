import { loadDecks } from '$lib/decks-content.server';
import { error } from '@sveltejs/kit';

export async function entries() {
  const decks = await loadDecks();
  return decks.map((d) => ({ slug: d.slug }));
}

export async function load({ params }) {
  const decks = await loadDecks();
  const deck = decks.find((d) => d.slug === params.slug);
  if (!deck) error(404, 'Deck not found');
  return { deck };
}
