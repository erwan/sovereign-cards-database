<script lang="ts">
  import type { Deck } from '$lib/decks-content';

  let { deck, coverSrc }: { deck: Deck; coverSrc: string } = $props();
</script>

<header class="deck-header">
  <img
    class="deck-header-cover"
    src={coverSrc}
    alt=""
    width="280"
    height="392"
    loading="eager"
  />
  <div class="deck-header-text">
    <h1 class="deck-title">{deck.displayName}</h1>
    {#if deck.description?.trim()}
      <p class="deck-description">{deck.description}</p>
    {/if}
  </div>
</header>
