import { DeckSchema } from "./schema";
import type { Deck } from "./decks-content";

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
