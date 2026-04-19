<script lang="ts">
  import SiteGitHubLink from '$lib/components/SiteGitHubLink.svelte';
  import { asset, resolve } from '$app/paths';
  import type { Asset } from '$app/types';

  let { data } = $props();
</script>

<svelte:head>
  <title>Sovereign Cards Database</title>
</svelte:head>

<main class="home">
  <div class="home-header">
    <h1>Sovereign: Fall of Wormwood</h1>
    <SiteGitHubLink />
  </div>
  <p class="lede">Cards database by faction. Choose a deck to browse card names and types.</p>
  <ul class="deck-grid">
    {#each data.decks as deck}
      <li>
        <a class="deck-link" href={resolve(`/factions/${deck.slug}`)}>
          <img
            class="deck-cover"
            src={asset(`/cards/${deck.slug}/cover.jpg` as Asset)}
            alt={deck.displayName}
            width="280"
            height="392"
            loading="lazy"
          />
        </a>
      </li>
    {/each}
  </ul>
  <div class="global-cta">
    <a class="cta-button" href={resolve('/cards')}>Browse All Cards</a>
    <p class="cta-description">Search and filter cards across all factions</p>
  </div>
</main>
