<script lang="ts" generics="T extends CardEntry">
  import CardListItem from './CardListItem.svelte';
  import type { CardEntry } from '$lib/decks-content';

  interface Props {
    cards: T[];
    totalCount: number;
    sortBy: 'cost' | 'name';
    view: 'list' | 'gallery';
    getImageSrc: (card: T) => string;
    getTypeLabel?: (card: T) => string;
  }

  let {
    cards,
    totalCount,
    sortBy = $bindable('cost'),
    view,
    getImageSrc,
    getTypeLabel,
  }: Props = $props();
</script>

<div class="filtered-card-list">
  <div class="result-count-row">
    <div class="result-count">
      {cards.length} of {totalCount} cards
    </div>
    <div class="sort-group">
      <label for="sort-by" class="sort-label">Sort by</label>
      <select id="sort-by" class="sort-select" bind:value={sortBy}>
        <option value="cost">Cost</option>
        <option value="name">Name</option>
      </select>
    </div>
  </div>

  {#if cards.length === 0}
    <div class="no-results">
      <p>No cards match your current filters.</p>
    </div>
  {:else}
    <ul class="card-list">
      {#each cards as card (card.name + ((card as Record<string, unknown>).factionSlug ?? ''))}
        <CardListItem
          {card}
          imageSrc={getImageSrc(card)}
          {view}
          typeLabel={getTypeLabel?.(card)}
        />
      {/each}
    </ul>
  {/if}
</div>

<style>
  .filtered-card-list {
    width: 100%;
  }

  .result-count-row {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.75rem 0;
  }

  .result-count {
    font-size: 0.875rem;
    color: var(--text-muted);
    font-weight: 500;
  }

  .sort-group {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .sort-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .sort-select {
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--border-strong);
    border-radius: 0.375rem;
    background: var(--bg-base);
    color: var(--text-primary);
    font-size: 0.875rem;
    font-family: inherit;
    min-width: 120px;
  }

  .sort-select:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 2px color-mix(in srgb, var(--accent) 35%, transparent);
  }

  .no-results {
    text-align: center;
    padding: 3rem;
    color: var(--text-muted);
  }
</style>
